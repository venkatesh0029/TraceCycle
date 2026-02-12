import { expect } from "chai";
import hre from "hardhat";
const { ethers } = hre;

describe("WasteTrace", function () {
    it("Should create a new waste record", async function () {
        const WasteTrace = await ethers.getContractFactory("WasteTrace");
        const wasteTrace = await WasteTrace.deploy();

        await wasteTrace.createWaste("Plastic");
        const waste = await wasteTrace.getWaste(1);

        expect(waste.wasteType).to.equal("Plastic");
        expect(waste.status).to.equal("Generated");
    });

    it("Should transfer waste", async function () {
        const [owner, otherAccount] = await ethers.getSigners();
        const WasteTrace = await ethers.getContractFactory("WasteTrace");
        const wasteTrace = await WasteTrace.deploy();

        await wasteTrace.createWaste("E-Waste");
        await wasteTrace.transferWaste(1, otherAccount.address);

        const waste = await wasteTrace.getWaste(1);
        expect(waste.owner).to.equal(otherAccount.address);
    });
});
