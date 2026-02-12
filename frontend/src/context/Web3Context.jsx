import React, { createContext, useContext, useState, useEffect } from 'react';
import { ethers } from 'ethers';
import WasteTraceABI from '../contracts/WasteTrace.json';

const Web3Context = createContext();

export const useWeb3 = () => useContext(Web3Context);

const CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3";

export const Web3Provider = ({ children }) => {
    const [currentAccount, setCurrentAccount] = useState("");
    const [contract, setContract] = useState(null);
    const [provider, setProvider] = useState(null);
    const [chainId, setChainId] = useState(null);

    useEffect(() => {
        checkWalletIsConnected();
        if (window.ethereum) {
            window.ethereum.on('accountsChanged', handleAccountsChanged);
            window.ethereum.on('chainChanged', handleChainChanged);
        }
        return () => {
            if (window.ethereum) {
                window.ethereum.removeListener('accountsChanged', handleAccountsChanged);
                window.ethereum.removeListener('chainChanged', handleChainChanged);
            }
        };
    }, []);

    const handleAccountsChanged = (accounts) => {
        if (accounts.length > 0) {
            setCurrentAccount(accounts[0]);
        } else {
            setCurrentAccount("");
            setContract(null);
        }
    };

    const handleChainChanged = () => {
        window.location.reload();
    };

    const checkWalletIsConnected = async () => {
        if (!window.ethereum) return;
        try {
            const accounts = await window.ethereum.request({ method: 'eth_accounts' });
            if (accounts.length > 0) {
                setCurrentAccount(accounts[0]);
                initializeContract();
            }
        } catch (error) {
            console.error("Error checking wallet connection:", error);
        }
    };

    const connectWallet = async () => {
        if (!window.ethereum) {
            alert("Please install MetaMask!");
            return;
        }
        try {
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            setCurrentAccount(accounts[0]);
            initializeContract();
        } catch (error) {
            console.error("Error connecting wallet:", error);
        }
    };

    const initializeContract = async () => {
        if (!window.ethereum) return;
        try {
            const provider = new ethers.BrowserProvider(window.ethereum);
            setProvider(provider);

            const signer = await provider.getSigner();
            const contract = new ethers.Contract(CONTRACT_ADDRESS, WasteTraceABI, signer);
            setContract(contract);

            const network = await provider.getNetwork();
            setChainId(network.chainId);

            console.log("Contract initialized:", contract);
        } catch (error) {
            console.error("Error initializing contract:", error);
        }
    };

    const createWaste = async (wasteType) => {
        try {
            if (!contract) return;
            console.log("Creating waste:", wasteType);
            const tx = await contract.createWaste(wasteType);
            await tx.wait();
            console.log("Waste created:", tx);
            return tx;
        } catch (error) {
            console.error("Error creating waste:", error);
            throw error;
        }
    };

    return (
        <Web3Context.Provider value={{
            connectWallet,
            currentAccount,
            contract,
            createWaste
        }}>
            {children}
        </Web3Context.Provider>
    );
};
