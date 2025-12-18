# Cryptographic Standards Research Document

**Version:** 1.0  
**Created:** December 18, 2025  
**Status:** Complete  
**Purpose:** Technical specification for high-assurance cryptography in Q-DNA  
**Cross-Reference:** Q-DNA Spec §4 (Security), §4.2 (Identity), §4.4 (Ledger Integrity)

---

## 1. Executive Summary

Q-DNA mandates a zero-trust cryptographic framework centered on:

- **Ed25519** for all digital signatures (Performance + Security)
- **W3C DIDs (did:key)** for decentralized agent identity
- **RFC 6962** compliant Merkle Hash Chains for ledger integrity
- **30-Day Automated Rotation** for all signing keys
- **NIST SP 800-57** lifecycle management

This report analyzes the theoretical foundations and implementation requirements for these mandates.

---

## 2. Key Management Framework (NIST SP 800-57)

Q-DNA adopts the lifecycle phases defined in NIST SP 800-57 Part 1 Revision 5.

### 2.1 Functional Classification

| Key Type                        | Role                             | Requirement                              |
| ------------------------------- | -------------------------------- | ---------------------------------------- |
| **Signing (Asymmetric)**        | Audit logs, Identity assertions  | Ed25519; Isolation in Secure Enclave/HSM |
| **Data Encryption (Symmetric)** | Bulk encryption at rest          | AES-256-GCM; Frequent rotation           |
| **Key Encryption (KEK)**        | Encrypting other keys (Wrapping) | Argon2id derived from passphrase         |

### 2.2 Lifecycle Phases

1. **Pre-Operational:** DRBG generation (32 bytes entropy), Registration (DID).
2. **Operational:** Active signing/decryption. Monitor for compromise.
3. **Post-Operational:** Verification only (historical data). Signing revoked.
4. **Destroyed:** Zeroization (overwrite memory/storage). Audit trail of destruction.

### 2.3 Cryptoperiods

Q-DNA enforces a **30-day cryptoperiod** to:

- Limit exposure of compromised keys (Blast Radius)
- Force operational rigor through automation
- Enable algorithm agility (easier migration to Post-Quantum)

---

## 3. Algorithm Selection: Why Ed25519?

Ed25519 is the mandated standard, superseding RSA and ECDSA.

### 3.1 Comparison Matrix

| Feature               | RSA-3072  | ECDSA (P-256) | Ed25519       | Q-DNA Result          |
| --------------------- | --------- | ------------- | ------------- | --------------------- |
| **Security Level**    | ~128-bit  | ~128-bit      | ~128-bit      | ✅ Match              |
| **Public Key Size**   | 384 bytes | 64 bytes      | **32 bytes**  | ✅ Minimal            |
| **Signature Size**    | 384 bytes | 64 bytes      | **64 bytes**  | ✅ Minimal            |
| **Deterministic?**    | No        | No            | **Yes**       | ✅ Safe from weak RNG |
| **Side-Channel Risk** | High      | High          | **Low**       | ✅ Constant-time      |
| **Signing Speed**     | Slow      | Fast          | **Very Fast** | ✅ High Throughput    |

**Key Advantage:** Ed25519 is deterministic; it derives the nonce by hashing the private key and message, eliminating the Sony PS3-style key recovery attack from weak RNGs.

---

## 4. 30-Day Key Rotation Mandate

Automation is mandatory. Human-managed rotation at this frequency is considered an operational risk.

### 4.1 Rollover Protocol (Grace Period)

- **Day T-5:** Generate $K_{new}$, publish public key to DID document.
- **T-5 to T:** Both keys valid for verification; $K_{current}$ still used for signing.
- **Day T:** Switch to signing with $K_{new}$.
- **Day T+5:** $K_{current}$ marked as retired (Verification Only).

### 4.2 Historical Verification

Long-term verification is handled by anchoring keys to the **Merkle Log Timestamp**. The public key archive preserves retired keys to verify old signatures, while their corresponding private keys are destroyed.

---

## 5. Audit Integrity: Merkle Hash Chains

To ensure the ledger is tamper-evident, Q-DNA implements a Binary Merkle Tree compliant with **RFC 6962**.

### 5.1 RFC 6962 Hashing Strategy

Protects against second preimage attacks (structural collisions):

- **Leaf Hash:** `SHA-256(0x00 || data)`
- **Internal Node:** `SHA-256(0x01 || Left || Right)`

### 5.2 Efficiency and Proofs

- **Inclusion Proof:** $O(\log n)$ efficiency. Prove entry exists without full log.
- **Consistency Proof:** Prove new tree is an append-only extension of old tree (prevents split-view attacks).
- **Signed Tree Head (STH):** Root hash signed every minute to anchor trust.

---

## 6. Decentralized Identity (DIDs)

Q-DNA uses **did:key** for serverless, location-agnostic identity.

### 6.1 Derivation (Ed25519)

1. Public Key (32 bytes)
2. Prepend Multicodec prefix for Ed25519: `0xed 0x01`
3. Multibase encode using Base58-BTC (prefix `z`)
4. **Example:** `did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK`

Resolution is purely local/mathematical; no blockchain or network lookup required.

---

## 7. Local Storage Security

### 7.1 Permissions

- **File:** `0600` (Owner Read/Write only)
- **Directory:** `0700` (Owner only)

### 7.2 Key Wrapping (Argon2id)

Private keys must never be stored in plaintext. They are wrapped using:

- **KDF:** Argon2id (Memory-hard to resist GPU cracking)
- **Parameters:** Min 64MB RAM, match hardware thread count
- **Cipher:** AES-256-GCM (Authenticated Encryption)

---

## 8. Compliance & Future-Proofing

- **Zero Trust:** Assume breach, verify explicitly, least privilege.
- **Post-Quantum Readiness:** Short rotation cycles enable rapid deployment of NIST ML-DSA (Dilithium) once finalized. `did:key` supports new multicodecs for hybrid signatures.

---

## References

[CRYPTO-001] NIST SP 800-57 Rev 5. "Recommendation for Key Management."  
[CRYPTO-002] RFC 8032. "Edwards-Curve Digital Signature Algorithm (EdDSA)."  
[CRYPTO-003] RFC 6962. "Certificate Transparency."  
[CRYPTO-004] W3C. "Decentralized Identifiers (DIDs) v1.0."  
[CRYPTO-005] Bernstein, D. J. "Ed25519: high-speed high-security signatures."  
[CRYPTO-006] NIST SP 800-132. "Recommendation for Password-Based Key Derivation."  
[CRYPTO-007] Argon2: IETF RFC 9106.  
[CRYPTO-008] C2PA. "Coalition for Content Provenance and Authenticity."
