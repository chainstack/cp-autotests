class NodeState:
    PENDING = "pending"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    DELETING = "deleting"
    DELETED = "deleted"

class NodePreset: 
    ETH_HOODIE = "gts.c.cp.presets.blockchain_preset.v1.0~c.cp.presets.evm_preset.v1.0~c.cp.presets.evm_reth_prysm.v1.0~c.cp.presets.eth_hoodi.v1.0"
    ETH_SEPOLIA = "gts.c.cp.presets.blockchain_preset.v1.0~c.cp.presets.evm_preset.v1.0~c.cp.presets.evm_reth_prysm.v1.0~c.cp.presets.eth_sepolia.v1.0"
    ETH_MAINNET = "gts.c.cp.presets.blockchain_preset.v1.0~c.cp.presets.evm_preset.v1.0~c.cp.presets.evm_reth_prysm.v1.0~c.cp.presets.ethereum_mainnet.v1.0"



class Node:
    def __init__(self, state: NodeState, preset: NodePreset):
        self.state = state
        self.preset = preset

    
    