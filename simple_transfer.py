"""
Simple example using the RoutingWrapper to route API request related
to the PoW to an offline full node but broadcasting the transactions
to a public full node.
"""
from iota import Iota
from iota.adapter.wrappers import RoutingWrapper

# a list of public nodes can be found here: http://iota.dance/nodes
PUBLIC_NODE = 'http://node03.iotatoken.nl:14265'

LOCAL_NODE = 'http://localhost:14265'

# insert your seed here
SEED = b'SEED9GOES9HERE'

API = Iota(
    RoutingWrapper(PUBLIC_NODE)
        .add_route('attachToTangle', LOCAL_NODE)
        .add_route('interruptAttachingToTangle', LOCAL_NODE),
    seed = SEED
    )

"""
Every function of API using attachToTangle or interruptAttachingToTangle
(e.g. API.send_transfer, API.attach_to_tangle, ...)
sends its attachToTangle- and interruptAttachingToTangle-commands to the local
full node and all other commands (like findTransactionsToApprove and
broadcastTransactions) to the public full node.
"""

from iota import ProposedBundle, ProposedTransaction, Address, Tag, TryteString

bundle = ProposedBundle()

output = ProposedTransaction(
    # receiving address of the transfer
    address = Address(
        b'ADDRESS9GOES9HERE99999999999999999999999999999999999TESTVALUE9DONTUSEINPRODUCTION'
        ),

    # Amount of Iota you want to send
    value = 1,

    # Optional Tag (27-trytes)
    tag = Tag(b'ROUTING9WRAPPER9WORKS'),

    # Message (2187-trytes)
    message = TryteString.from_string('I used iota.adapter.wrappers.RoutingWrapper.')
    )

bundle.add_transaction(output)


"""
A ProposedBundle is a Bundle that is not yet attached to the Tangle.
A ProposedTransaction is a Transaction that is not yet attached to the Tangle.
"""

print("Sending transfer...")

response = API.send_transfer(3, bundle)

print('Bundle Hash: '+ response['bundle'].hash.as_json_compatible())

"""
The API.send_transfer function will take care of signing and inserting the
input transaction and remainder transaction.
I'm printing the bundle hash which can be used for reattaching if necessary.
"""
