const hre = require("hardhat");

async function main() {
    const WasteTrace = await hre.ethers.getContractFactory("WasteTrace");
    const wasteTrace = await WasteTrace.deploy();

    await wasteTrace.waitForDeployment();

    console.log(
        `WasteTrace deployed to ${await wasteTrace.getAddress()}`
    );
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
