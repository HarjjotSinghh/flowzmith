import { useQuery, useMutation } from "convex/react";
import { api } from "../convex/_generated/api";
import { Id } from "../convex/_generated/dataModel";

// Hook for starting a deployment
export function useStartDeployment() {
  return useMutation(api.deployments.startDeployment);
}

// Hook for updating deployment status
export function useUpdateDeploymentStatus() {
  return useMutation(api.deployments.updateDeploymentStatus);
}

// Hook for getting a specific deployment
export function useDeployment(id: Id<"deployments"> | undefined) {
  return useQuery(api.deployments.getDeployment, id ? { id } : "skip");
}

// Hook for getting contract deployments
export function useContractDeployments(
  contractId: Id<"contracts"> | undefined,
  limit?: number
) {
  return useQuery(
    api.deployments.getContractDeployments,
    contractId ? { contractId, limit } : "skip"
  );
}

// Hook for getting user deployments
export function useUserDeployments(limit?: number, status?: string) {
  return useQuery(api.deployments.getUserDeployments, { limit, status });
}

// Hook for getting deployment statistics
export function useDeploymentStats(timeframe?: string) {
  return useQuery(api.deployments.getDeploymentStats, { timeframe });
}

// Hook for getting recent deployment activity
export function useRecentDeploymentActivity(limit?: number) {
  return useQuery(api.deployments.getRecentDeploymentActivity, { limit });
}

// Hook for canceling a deployment
export function useCancelDeployment() {
  return useMutation(api.deployments.cancelDeployment);
}