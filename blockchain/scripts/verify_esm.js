
import hre from "hardhat";

async function main() {
    console.log("Hardhat ESM loading successful!");
    console.log("Network:", hre.network.name);

    // Check if we can get contract factory (requires compilation to have worked)
    try {
        const WasteTrace = await hre.ethers.getContractFactory("WasteTrace");
        console.log("Contract factory loaded successfully.");
    } catch (error) {
        console.error("Failed to load contract factory:", error);
        process.exit(1);
    }
}

main().catch((error) => {
    console.error(error);
    process.exit(1);
});
