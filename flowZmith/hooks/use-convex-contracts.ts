import { useQuery, useMutation } from "convex/react";
import { api } from "../convex/_generated/api";
import { Id } from "../convex/_generated/dataModel";

// Hook for getting user contracts
export function useUserContracts(limit?: number, status?: string) {
  return useQuery(api.contracts.getUserContracts, { limit, status });
}

// Hook for getting public contracts
export function usePublicContracts(limit?: number, network?: string) {
  return useQuery(api.contracts.getPublicContracts, { limit, network });
}

// Hook for getting a specific contract
export function useContract(id: Id<"contracts"> | undefined) {
  return useQuery(api.contracts.getContract, id ? { id } : "skip");
}

// Hook for creating a contract
export function useCreateContract() {
  return useMutation(api.contracts.createContract);
}

// Hook for updating a contract
export function useUpdateContract() {
  return useMutation(api.contracts.updateContract);
}

// Hook for adding a collaborator
export function useAddCollaborator() {
  return useMutation(api.contracts.addCollaborator);
}

// Hook for searching contracts
export function useSearchContracts(query: string, limit?: number) {
  return useQuery(
    api.contracts.searchContracts,
    query ? { query, limit } : "skip"
  );
}

// Hook for deleting a contract
export function useDeleteContract() {
  return useMutation(api.contracts.deleteContract);
}

// Hook for getting contract analytics
export function useContractAnalytics(contractId: Id<"contracts"> | undefined) {
  return useQuery(
    api.contracts.getContractAnalytics,
    contractId ? { contractId } : "skip"
  );
}