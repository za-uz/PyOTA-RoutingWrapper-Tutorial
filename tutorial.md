This is a tutorial explaining how to use the `iota.adapter.wrappers.RoutingWrapper`.

As someone once said:

> Getting started is the most difficult part of any newly introduced revolutionary technology.

And [this tutorial](https://medium.com/@johngrant/iota-python-a-beginning-8067f29a7e0) by [John Grant](https://medium.com/@johngrant) really helped me getting started experimenting with the Python library of IOTA. I tried to make a more detailed tutorial that shows how to make a transfer and reattach it using the pyota RoutingWrapper.

# Run an offline full node

Your local "full node" does not require any special setting up. Its only purpose is to do the Proof of Work. **You don't need to worry about being online 24/7 or finding neighbours.**

* download and install [Java](www.java.com/download/) (if you don't have it already)
  * try `java -version` to check whether you have it or not


* download the [*latest release* of the IRI](https://github.com/iotaledger/iri/releases) (`iri-1.4.1.4.jar` in my case)

* create an empty directory and put the `iri-<version>.jar` into it

* now you can start it with

  ```bash
  java -jar iri-1.4.1.4.jar -p 14265
  ```

  You will see

  ```
  12/26 13:03:50.612 [main] INFO  com.iota.iri.IRI - IOTA Node initialised correctly.
  ```

  but you don't have to worry about that. Once messages like this:

  ```
  12/26 13:05:50.449 [pool-2-thread-2] INFO  com.iota.iri.network.Node - toProcess = 0 , toBroadcast = 0 , toRequest = 0 , toReply = 0 / totalTransactions = 0
  12/26 13:06:00.450 [pool-2-thread-2] INFO  com.iota.iri.network.Node - toProcess = 0 , toBroadcast = 0 , toRequest = 0 , toReply = 0 / totalTransactions = 0
  12/26 13:06:10.451 [pool-2-thread-2] INFO  com.iota.iri.network.Node - toProcess = 0 , toBroadcast = 0 , toRequest = 0 , toReply = 0 / totalTransactions = 0
  ```

  start to pop up, your node is ready to receive `attachToTangle`-commands and do the POW for you.

# Simple Transfer

You will need the PyOTA Library which can be installed with [`pip install pyota`](https://pypi.python.org/pypi/pip/) or by following the instructions [here](https://github.com/iotaledger/iota.lib.py).

I created a new folder *`iota-routing-wrapper-tutorial`* containing 2 python files: `simple_transfer.py` and `reattach.py`

## `simple_transfer.py`

### Routing Wrapper

```python
"""
Simple example using the RoutingWrapper to route API request related
to the PoW to an offline full node but broadcasting the transactions
to a public full node.
"""
from iota import Iota
from iota.adapter.wrappers import RoutingWrapper

# a list of public nodes can be found here: http://iota.dance/nodes
PUBLIC_NODE = 'https://iotanode.us:443'

LOCAL_NODE = 'http://localhost:14265'

# insert your seed here
SEED = b'SEED9GOES9HERE'

API = Iota(
    RoutingWrapper(PUBLIC_NODE)
        .add_route('attachToTangle', LOCAL_NODE)
        .add_route('interruptAttachingToTangle', LOCAL_NODE),
    seed = SEED
    )
```

Every function of `API` using `attachToTangle` or `interruptAttachingToTangle` (e.g. `API.send_transfer`, `API.attach_to_tangle`, ...) sends its `attachToTangle`- and `interruptAttachingToTangle`-commands to the local full node and all other commands (like `findTransactionsToApprove` and `broadcastTransactions`) to the public full node.

### Proposed Bundle

```python
from iota import ProposedBundle, ProposedTransaction, Address, Tag, TryteString

bundle = ProposedBundle()

output = ProposedTransaction(
    # receiving address of the transfer
    address = Address(
        #b'ADDRESS9GOES9HERE99999999999999999999999999999999999TESTVALUE9DONTUSEINPRODUCTION'
    	),

    # Amount of Iota you want to send
    value = 1,

    # Optional Tag (27-trytes)
    tag = Tag(b'ROUTING9WRAPPER9WORKS'),

    # Message (2187-trytes)
    message = TryteString.from_string('I used iota.adapter.wrappers.RoutingWrapper.')
    )

bundle.add_transaction(output)
```
A `ProposedBundle` is a Bundle that is not yet attached to the Tangle.
A `ProposedTransaction` is a Transaction that is not yet attached to the Tangle.

###Send Transfer

```python
print("Sending transfer...")

response = API.send_transfer(3, bundle)

print('Bundle Hash: '+ response['bundle'].hash)
```

The API.send_transfer function will take care of **signing** and inserting the **input transaction(s)** and **remainder transaction**. I'm printing the bundle hash which can be used for **reattaching** if necessary.

## `reattach.py`

```python
"""
Reattaching with RoutingWrapper
"""
from iota import Iota
from iota.adapter.wrappers import RoutingWrapper

# a list of public nodes can be found here: http://iota.dance/nodes
PUBLIC_NODE = 'http://node.iota.bar:14265'

LOCAL_NODE = 'http://localhost:14265'

API = Iota(
    RoutingWrapper(PUBLIC_NODE)
        .add_route('attachToTangle', LOCAL_NODE)
        .add_route('interruptAttachingToTangle', LOCAL_NODE)
    )
```
To reattach a bundle, I initialize the Iota API with `RoutingWrapper` like I did before. Then I prompt the user to  input the bundle hash of the bundle they want to reattach.

```python
bundle_hash = input('Paste bundle hash: ')
```
Since `API.replay_bundle` does not accept a bundle hash as argument, I have to pass the transaction hash with a `currentIndex` of 0 (= the first transaction or "tail transaction" of a bundle).
That's why we have to **get the transaction hashes of the bundle** with `API.find_transactions`. Then we have to find out which of the returned transactions has a `currentIndex` of 0.

```python
transaction_hashes = API.find_transactions(bundles=[bundle_hash])['hashes']
```

`transaction_hashes` is a list that contains `TransactionHash`-Objects. To get the whole transactions from those Transaction Hashes, I use `API.get_trytes()`:

```python
bundle_trytes = API.get_trytes(transaction_hashes)['trytes']
```

`bundle_trytes` is a list that contains `TryteString`-Objects. These TryteStrings are the raw transaction data which can be *casted* into `Transaction`-Objects with ``Transaction.from_tryte_string()`

```python
from iota import Transaction

for transaction_trytes in bundle_trytes:
    transaction = Transaction.from_tryte_string(transaction_trytes)
    if transaction.is_tail:
        print('Reattaching...')
        API.replay_bundle(transaction.hash, 3)
        print('Reattached')
        break
```

Once the tail transaction is found, I call `API.replay_bundle()` to reattach the bundle and break out of the for-loop.

# Version

This Tutorial was tested with

* IRI 1.4.1.4 and IRI 1.4.1.6
* Python 3.6.1
* PyOTA (2.0.2)



# Sources

[Medium - IOTA & Python - A Beginning - John Grant](https://medium.com/@johngrant/iota-python-a-beginning-8067f29a7e0)

[Github Adapter Documentation](https://github.com/iotaledger/documentation/blob/iota.lib.py/1.2.x/source/includes/_adapters.md)

[Github Types Documentation](https://github.com/iotaledger/documentation/blob/iota.lib.py/1.2.x/source/includes/_types.md)

