import Foundation
import CryptoKit
import Security

// macOS 13+. No external dependencies. v1 recovery secret is 32 random bytes
// represented as hex, NOT a BIP-39 mnemonic.
struct Envelope: Codable {
    let version: Int
    let id: String
    let ephemeralPublic: Data
    let deviceWrap: Data
    let recoveryWrap: Data
    let payload: Data
}
enum VaultError: Error { case usage, invalid, exists, noHardware }
func random(_ count: Int) throws -> Data {
    var data = Data(count: count)
    let status = data.withUnsafeMutableBytes { SecRandomCopyBytes(kSecRandomDefault, count, $0.baseAddress!) }
    guard status == errSecSuccess else { throw VaultError.invalid }
    return data
}
func writeNew(_ data: Data, _ url: URL) throws {
    let fd = open(url.path, O_WRONLY | O_CREAT | O_EXCL, S_IRUSR | S_IWUSR)
    guard fd >= 0 else { throw VaultError.exists }
    defer { close(fd) }
    try data.withUnsafeBytes { bytes in
        var offset = 0
        while offset < bytes.count {
            let n = Darwin.write(fd, bytes.baseAddress!.advanced(by: offset), bytes.count - offset)
            guard n > 0 else { throw VaultError.invalid }
            offset += n
        }
    }
    guard fsync(fd) == 0 else { throw VaultError.invalid }
}
func loadSeed(_ url: URL) throws -> SymmetricKey {
    let s = try String(contentsOf: url, encoding: .utf8).trimmingCharacters(in: .whitespacesAndNewlines)
    guard s.count == 64, s.allSatisfy({ $0.isHexDigit }) else { throw VaultError.invalid }
    let bytes = stride(from: 0, to: 64, by: 2).map { UInt8(s[s.index(s.startIndex, offsetBy: $0)..<s.index(s.startIndex, offsetBy: $0+2)], radix: 16)! }
    let seed = SymmetricKey(data: Data(bytes))
    return HKDF<SHA256>.deriveKey(inputKeyMaterial: seed, salt: Data("vault-recovery-salt-v1".utf8), info: Data("crypto-autoresearcher/recovery/v1".utf8), outputByteCount: 32)
}
func seal(_ plaintext: Data, _ key: SymmetricKey, _ aad: Data) throws -> Data {
    let box = try AES.GCM.seal(plaintext, using: key, authenticating: aad)
    return box.combined!
}
func openBox(_ data: Data, _ key: SymmetricKey, _ aad: Data) throws -> Data {
    guard let box = try? AES.GCM.SealedBox(combined: data) else { throw VaultError.invalid }
    return try AES.GCM.open(box, using: key, authenticating: aad)
}
func deviceKey(_ directory: URL) throws -> SecureEnclave.P256.KeyAgreement.PrivateKey {
    let representation = try Data(contentsOf: directory.appendingPathComponent("device.keyref"))
    return try SecureEnclave.P256.KeyAgreement.PrivateKey(dataRepresentation: representation)
}
func aad(_ id: String, _ purpose: String) -> Data { Data("vault/v1/\(id)/\(purpose)".utf8) }
func main() throws {
    let a = CommandLine.arguments
    guard a.count >= 3 else { throw VaultError.usage }
    let cmd = a[1]
    let directory = URL(fileURLWithPath: a[2], isDirectory: true)
    if cmd == "init" {
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        guard SecureEnclave.isAvailable else { throw VaultError.noHardware }
        let device = try SecureEnclave.P256.KeyAgreement.PrivateKey()
        let seed = try random(32)
        try writeNew(device.dataRepresentation, directory.appendingPathComponent("device.keyref"))
        try writeNew(Data((seed.map { String(format: "%02x", $0) }.joined() + "\n").utf8), directory.appendingPathComponent("recovery.hex"))
        print("Initialized. MOVE recovery.hex to OFFLINE storage; remove it from the vault directory before using the vault.")
    } else if cmd == "encrypt" {
        guard a.count == 5 else { throw VaultError.usage }
        let source = URL(fileURLWithPath: a[3]), dest = URL(fileURLWithPath: a[4])
        let recovery = try loadSeed(directory.appendingPathComponent("recovery.hex"))
        let device = try deviceKey(directory)
        let ephemeral = P256.KeyAgreement.PrivateKey()
        let secret = try ephemeral.sharedSecretFromKeyAgreement(with: device.publicKey)
        let wrapKey = secret.hkdfDerivedSymmetricKey(using: SHA256.self, salt: Data("vault-device-v1".utf8), sharedInfo: Data("crypto-autoresearcher/device-wrap/v1".utf8), outputByteCount: 32)
        let id = UUID().uuidString
        let dek = SymmetricKey(data: try random(32))
        let keyData = dek.withUnsafeBytes { Data($0) }
        let envelope = Envelope(version: 1, id: id, ephemeralPublic: ephemeral.publicKey.rawRepresentation,
            deviceWrap: try seal(keyData, wrapKey, aad(id, "device")),
            recoveryWrap: try seal(keyData, recovery, aad(id, "recovery")),
            payload: try seal(Data(contentsOf: source), dek, aad(id, "payload")))
        try writeNew(JSONEncoder().encode(envelope), dest)
        print("Encrypted \(id)")
    } else if cmd == "decrypt" || cmd == "recover" {
        guard a.count == 5 else { throw VaultError.usage }
        let envelope = try JSONDecoder().decode(Envelope.self, from: Data(contentsOf: URL(fileURLWithPath: a[3])))
        guard envelope.version == 1 else { throw VaultError.invalid }
        let keyData: Data
        if cmd == "recover" {
            keyData = try openBox(envelope.recoveryWrap, loadSeed(directory.appendingPathComponent("recovery.hex")), aad(envelope.id, "recovery"))
        } else {
            let device = try deviceKey(directory)
            let peer = try P256.KeyAgreement.PublicKey(rawRepresentation: envelope.ephemeralPublic)
            let secret = try device.sharedSecretFromKeyAgreement(with: peer)
            let key = secret.hkdfDerivedSymmetricKey(using: SHA256.self, salt: Data("vault-device-v1".utf8), sharedInfo: Data("crypto-autoresearcher/device-wrap/v1".utf8), outputByteCount: 32)
            keyData = try openBox(envelope.deviceWrap, key, aad(envelope.id, "device"))
        }
        let plaintext = try openBox(envelope.payload, SymmetricKey(data: keyData), aad(envelope.id, "payload"))
        try writeNew(plaintext, URL(fileURLWithPath: a[4]))
        print("Decrypted \(envelope.id)")
    } else { throw VaultError.usage }
}
do { try main() } catch {
    fputs("Vault error: \(error). Usage: vault init DIR | vault encrypt DIR IN OUT | vault decrypt DIR IN OUT | vault recover DIR IN OUT\n", stderr)
    exit(1)
}
