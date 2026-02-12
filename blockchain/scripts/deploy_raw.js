const { ethers } = require("ethers");
const fs = require("fs");
const path = require("path");

async function main() {
    const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
    const signer = await provider.getSigner();

    const artifactPath = path.join(__dirname, "../artifacts/contracts/WasteTrace.sol/WasteTrace.json");
    const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));

    const factory = new ethers.ContractFactory(artifact.abi, artifact.bytecode, signer);
    console.log("Deploying...");
    const contract = await factory.deploy();

    await contract.waitForDeployment();
    const address = await contract.getAddress();

    console.log(`Deployed to: ${address}`);
}

main().catch((error) => {
    console.error(error);
    process.exit(1);
});
