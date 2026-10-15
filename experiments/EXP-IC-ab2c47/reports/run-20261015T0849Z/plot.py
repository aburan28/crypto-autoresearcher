from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parent;x=json.loads((p/'summary.json').read_text())
fig,axes=plt.subplots(1,2,figsize=(10,3.8),layout='constrained')
rows=x['height'];axes[0].bar([str(v['W']) for v in rows],[v['nonempty_after'] for v in rows],color=['#487b99']*5+['#9b7c46'])
axes[0].axhline(22,color='#666',linestyle=':',label='22 nonempty before filtering')
axes[0].set(xlabel='Strict centered-coordinate bound W',ylabel='Nonempty fibers / 146',title='Actual complete-chain retention',ylim=(0,26));axes[0].legend(fontsize=7)
labels=['strict\ncertificate','zero-dim\nideal','verified\nroot','positive\nnew rank'];values=[x['strict_certificate_cells'],x['zero_dimensional_cells'],x['valid_root_cells'],x['positive_marginal_rank_cells']]
axes[1].bar(labels,values,color=['#487b99','#698a5c','#9b7c46','#9b7c46']);axes[1].set(ylabel='Cells / 576 finite-target arm cells',title='Different gates; short vectors are not relations')
for i,v in enumerate(values):axes[1].text(i,v+6,str(v),ha='center',fontsize=8)
fig.suptitle('RUN-IC-c497d3; one deterministic fixed schedule; W=97 is the whole-field control',fontsize=10)
fig.savefig(p/'measurements.svg')
