"""
Reattaching with RoutingWrapper
"""
from iota import Iota
from iota.adapter.wrappers import RoutingWrapper

# a list of public nodes can be found here: http://iota.dance/nodes
PUBLIC_NODE = 'http://176.9.3.149:14265'

LOCAL_NODE = 'http://localhost:14265'

API = Iota(
    RoutingWrapper(PUBLIC_NODE)
        .add_route('attachToTangle', LOCAL_NODE)
        .add_route('interruptAttachingToTangle', LOCAL_NODE)
    )

bundle_hash = input('Paste bundle hash: ')

"""
API.replay_bundle does not accept a bundle hash as argument. You have to pass
the transaction hash with a currentIndex of 0 (= the first transaction or "tail transaction" of a
bundle).
That's why we have to get the transaction hashes of the bundle with
API.find_transactions. Then we have to find out which of the returned
transactions has a currentIndex of 0.
"""

print('Fetching transaction hashes...')
transaction_hashes = API.find_transactions(bundles=[bundle_hash])['hashes']
print('Received transaction hashes.')


print('Fetching transaction trytes...')
bundle_trytes = API.get_trytes(transaction_hashes)['trytes']
print('Received transaction trytes.')

from iota import Transaction

for transaction_trytes in bundle_trytes:
    transaction = Transaction.from_tryte_string(transaction_trytes)
    if transaction.is_tail:
        print('Reattaching...')
        API.replay_bundle(transaction.hash, 3)
        print('Reattached')
        break
