import sys

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory

from secp256k1 import PrivateKey

context = create_context('secp256k1')
private_key = context.new_random_private_key()
signer = CryptoFactory(context).new_signer(private_key)
public_key = signer.get_public_key()


if len(sys.argv) > 1:
    if sys.argv[1] == "private":
        print(private_key.as_hex())
        exit(0)
    elif sys.argv[1] == "public":
        print(private_key.as_hex())
        exit(0)

print("Public :", public_key.as_hex())
print("Private:", private_key.as_hex())