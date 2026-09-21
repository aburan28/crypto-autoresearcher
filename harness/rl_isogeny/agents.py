"""Agents and the training loop (harness.rl_isogeny).

Three agents, one interface:

    act(obs, mask, key, greedy) -> action
    observe(...)                (per-step learning signal; no-op for random)
    end_episode()

RandomAgent     uniform over valid actions; the paired baseline every claim is
                measured against.
TabularQAgent   standard-library Q-learning over the environment's discrete
                state key (neighbour-count pattern, Legendre flags, presentation
                indices, identity bits).  Deterministic in its seed.
PPOAgent        clipped PPO with GAE on a two-layer MLP, torch only; action
                masking by logit suppression; deterministic in its seed on CPU.
                lr = 1e-3 by default: at 3e-4 the sampled policy reaches the
                planted needle but its argmax stalls (probe in DESIGN.md 6).

``train`` runs episodes and returns one record per episode; ``evaluate`` runs
greedy episodes.  Records carry the TRUE score even when the environment is in
permuted mode, so a permuted run can be judged on the real objective.
"""
from __future__ import annotations

import math
import random
import time
from typing import Any, Dict, List, Optional, Sequence

from .env import IsogenyPDPEnv


class RandomAgent:
    name = "random"
    trainable = False

    def __init__(self, seed: int = 0):
        self.rng = random.Random(seed)

    def act(self, obs: Sequence[float], mask: Sequence[bool], key: Any = None, greedy: bool = False) -> int:
        valid = [i for i, ok in enumerate(mask) if ok]
        return self.rng.choice(valid)

    def observe(self, *args, **kwargs) -> None:
        pass

    def end_episode(self) -> None:
        pass


class TabularQAgent:
    name = "tabular_q"
    trainable = True

    def __init__(self, n_actions: int, seed: int = 0, alpha: float = 0.3, gamma: float = 0.95,
                 eps_start: float = 0.5, eps_end: float = 0.05, eps_episodes: int = 100):
        self.n_actions = n_actions
        self.rng = random.Random(seed)
        self.alpha, self.gamma = alpha, gamma
        self.eps_start, self.eps_end, self.eps_episodes = eps_start, eps_end, eps_episodes
        self.episode = 0
        self.Q: Dict[Any, List[float]] = {}

    def _q(self, key: Any) -> List[float]:
        q = self.Q.get(key)
        if q is None:
            q = [0.0] * self.n_actions
            self.Q[key] = q
        return q

    @property
    def epsilon(self) -> float:
        frac = min(1.0, self.episode / max(1, self.eps_episodes))
        return self.eps_start + (self.eps_end - self.eps_start) * frac

    def act(self, obs: Sequence[float], mask: Sequence[bool], key: Any = None, greedy: bool = False) -> int:
        valid = [i for i, ok in enumerate(mask) if ok]
        if not greedy and self.rng.random() < self.epsilon:
            return self.rng.choice(valid)
        q = self._q(key)
        best = max(q[i] for i in valid)
        top = [i for i in valid if q[i] == best]
        return top[0] if greedy else self.rng.choice(top)

    def observe(self, key: Any, action: int, reward: float, next_key: Any,
                next_mask: Sequence[bool], done: bool) -> None:
        q = self._q(key)
        target = reward
        if not done:
            nq = self._q(next_key)
            target += self.gamma * max(nq[i] for i, ok in enumerate(next_mask) if ok)
        q[action] += self.alpha * (target - q[action])

    def end_episode(self) -> None:
        self.episode += 1


class PPOAgent:
    name = "ppo"
    trainable = True

    def __init__(self, obs_dim: int, n_actions: int, seed: int = 0, hidden: int = 64, lr: float = 1e-3,
                 gamma: float = 0.95, lam: float = 0.9, clip: float = 0.2, epochs: int = 4,
                 minibatch: int = 64, entropy_coef: float = 0.01, value_coef: float = 0.5,
                 update_every: int = 8, max_grad_norm: float = 0.5):
        try:
            import torch
            import torch.nn as nn
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise ImportError("PPOAgent needs torch (pip install -e '.[rl]'); use tabular_q instead") from exc
        self.torch = torch
        torch.manual_seed(seed)
        torch.set_num_threads(1)
        self.rng = random.Random(seed)
        self.obs_dim, self.n_actions = obs_dim, n_actions
        self.gamma, self.lam, self.clip = gamma, lam, clip
        self.epochs, self.minibatch = epochs, minibatch
        self.entropy_coef, self.value_coef = entropy_coef, value_coef
        self.update_every, self.max_grad_norm = update_every, max_grad_norm
        self.policy = nn.Sequential(nn.Linear(obs_dim, hidden), nn.Tanh(), nn.Linear(hidden, hidden),
                                    nn.Tanh(), nn.Linear(hidden, n_actions))
        self.value = nn.Sequential(nn.Linear(obs_dim, hidden), nn.Tanh(), nn.Linear(hidden, hidden),
                                   nn.Tanh(), nn.Linear(hidden, 1))
        self.opt = torch.optim.Adam(list(self.policy.parameters()) + list(self.value.parameters()), lr=lr)
        self.buffer: List[dict] = []
        self.episodes_since_update = 0
        self.updates = 0
        self.last_stats: Dict[str, float] = {}

    def _dist(self, obs, mask):
        torch = self.torch
        logits = self.policy(obs)
        logits = logits.masked_fill(~mask, -1e9)
        return torch.distributions.Categorical(logits=logits)

    def act(self, obs: Sequence[float], mask: Sequence[bool], key: Any = None, greedy: bool = False) -> int:
        torch = self.torch
        with torch.no_grad():
            o = torch.tensor(obs, dtype=torch.float32)
            m = torch.tensor(mask, dtype=torch.bool)
            dist = self._dist(o, m)
            if greedy:
                action = int(torch.argmax(dist.probs).item())
            else:
                action = int(dist.sample().item())
            self._last = (o, m, dist.log_prob(torch.tensor(action)).item(), self.value(o).item())
        return action

    def observe(self, key: Any, action: int, reward: float, next_key: Any,
                next_mask: Sequence[bool], done: bool) -> None:
        o, m, logp, v = self._last
        self.buffer.append({"obs": o, "mask": m, "action": action, "logp": logp, "value": v,
                            "reward": float(reward), "done": bool(done)})

    def end_episode(self) -> None:
        self.episodes_since_update += 1
        if self.episodes_since_update >= self.update_every:
            self.update()

    def update(self) -> None:
        torch = self.torch
        if not self.buffer:
            return
        n = len(self.buffer)
        rewards = [t["reward"] for t in self.buffer]
        values = [t["value"] for t in self.buffer]
        dones = [t["done"] for t in self.buffer]
        adv = [0.0] * n
        last = 0.0
        for i in reversed(range(n)):
            next_v = 0.0 if (dones[i] or i == n - 1) else values[i + 1]
            delta = rewards[i] + self.gamma * next_v - values[i]
            last = delta + (0.0 if dones[i] else self.gamma * self.lam * last)
            adv[i] = last
        returns = [a + v for a, v in zip(adv, values)]
        obs = torch.stack([t["obs"] for t in self.buffer])
        masks = torch.stack([t["mask"] for t in self.buffer])
        actions = torch.tensor([t["action"] for t in self.buffer])
        old_logp = torch.tensor([t["logp"] for t in self.buffer], dtype=torch.float32)
        adv_t = torch.tensor(adv, dtype=torch.float32)
        if n > 1:
            adv_t = (adv_t - adv_t.mean()) / (adv_t.std() + 1e-8)
        ret_t = torch.tensor(returns, dtype=torch.float32)
        idx = list(range(n))
        stats = {"policy_loss": 0.0, "value_loss": 0.0, "entropy": 0.0, "batches": 0}
        for _ in range(self.epochs):
            self.rng.shuffle(idx)
            for s in range(0, n, self.minibatch):
                mb = torch.tensor(idx[s:s + self.minibatch])
                dist = self._dist(obs[mb], masks[mb])
                logp = dist.log_prob(actions[mb])
                ratio = torch.exp(logp - old_logp[mb])
                a = adv_t[mb]
                pl = -torch.min(ratio * a, torch.clamp(ratio, 1 - self.clip, 1 + self.clip) * a).mean()
                vl = ((self.value(obs[mb]).squeeze(-1) - ret_t[mb]) ** 2).mean()
                ent = dist.entropy().mean()
                loss = pl + self.value_coef * vl - self.entropy_coef * ent
                self.opt.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(list(self.policy.parameters()) + list(self.value.parameters()),
                                               self.max_grad_norm)
                self.opt.step()
                stats["policy_loss"] += pl.item()
                stats["value_loss"] += vl.item()
                stats["entropy"] += ent.item()
                stats["batches"] += 1
        b = max(1, stats["batches"])
        self.last_stats = {k: (v / b if k != "batches" else v) for k, v in stats.items()}
        self.buffer = []
        self.episodes_since_update = 0
        self.updates += 1


def make_agent(name: str, env: IsogenyPDPEnv, seed: int = 0, **kw):
    if name == "random":
        return RandomAgent(seed)
    if name == "tabular_q":
        return TabularQAgent(env.n_actions, seed, **kw)
    if name == "ppo":
        return PPOAgent(env.obs_dim, env.n_actions, seed, **kw)
    raise ValueError(f"unknown agent {name}")


def run_episode(env: IsogenyPDPEnv, agent, greedy: bool = False, learn: bool = True,
                keep_trajectory: bool = True) -> dict:
    t0 = time.time()
    obs = env.reset()
    key = env.discrete_key()
    mask = env.action_mask()
    ret = 0.0
    true_ret = 0.0
    trajectory: List[str] = []
    done = False
    while not done:
        action = agent.act(obs, mask, key, greedy=greedy)
        obs, reward, done, info = env.step(action)
        next_key = env.discrete_key()
        next_mask = env.action_mask()
        if learn and agent.trainable:
            agent.observe(key, action, reward, next_key, next_mask, done)
        ret += reward
        true_ret += info["true_reward"]
        trajectory.append(info["action"])
        key, mask = next_key, next_mask
    if learn and agent.trainable:
        agent.end_episode()
    return {
        "return": ret, "true_return": true_ret, "final_score": env.score,
        "start_score": env.start_score, "best_score": env.best_score, "best_state": env.best_state,
        "final_state": env._state_record(env.planted_target is not None
                                         and env.state_key() == env.planted_target),
        "planted_hit": env.planted_hit, "steps": env.steps, "seconds": time.time() - t0,
        "trajectory": trajectory if keep_trajectory else None,
    }


def train(env: IsogenyPDPEnv, agent, episodes: int, log=None) -> List[dict]:
    records = []
    for ep in range(episodes):
        rec = run_episode(env, agent, greedy=False, learn=True, keep_trajectory=False)
        rec["episode"] = ep
        rec.pop("trajectory", None)
        rec["best_state"] = {"spec": rec["best_state"]["spec"], "j": rec["best_state"]["curve"]["j"]}
        rec["final_state"] = {"spec": rec["final_state"]["spec"], "j": rec["final_state"]["curve"]["j"]}
        rec["evaluations"] = env.meter.evaluations
        if hasattr(agent, "epsilon"):
            rec["epsilon"] = agent.epsilon
        if getattr(agent, "last_stats", None):
            rec["ppo"] = dict(agent.last_stats)
        records.append(rec)
        if log and (ep % max(1, episodes // 10) == 0 or ep == episodes - 1):
            log(f"  [{agent.name}] ep {ep:4d} return {rec['true_return']:+.3f} best {rec['best_score']:+.3f} "
                f"final {rec['final_score']:+.3f} hit={rec['planted_hit']} evals={env.meter.evaluations}")
    return records


def evaluate(env: IsogenyPDPEnv, agent, episodes: int, greedy: bool = True) -> List[dict]:
    """Greedy (argmax / epsilon = 0) or stochastic (the policy as trained, no
    learning) evaluation episodes.  Both are reported: a PPO policy regularised
    by an entropy bonus can be near-optimal when sampled while its argmax stalls
    on a local optimum, and the difference is part of the reading."""
    out = []
    for ep in range(episodes):
        rec = run_episode(env, agent, greedy=greedy, learn=False)
        rec["episode"] = ep
        rec["mode"] = "greedy" if greedy else "stochastic"
        out.append(rec)
    return out
