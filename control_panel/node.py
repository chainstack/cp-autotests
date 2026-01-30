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

class NodeProtocol:
    ETH_HOODIE = "Ethereum Hoodi Reth Prysm"
    ETH_SEPOLIA = "Ethereum Sepolia Reth Prysm"
    ETH_MAINNET = "Ethereum Mainnet Reth Prysm"

class NodeConfig:
    ETH_SEPOLIA_NANO = "Ethereum Sepolia Reth Prysm Nano"
    ETH_MAINNET_NANO = "Ethereum Mainnet Reth Prysm Nano"
    ETH_HOODIE_NANO = "Ethereum Hoodi Reth Prysm Nano"
    

class Node:
    def __init__(self, state: NodeState, preset: NodePreset, protocol: NodeProtocol, config: NodeConfig):
        self.state = state
        self.preset = preset
        self.protocol = protocol
        self.config = config

    
    