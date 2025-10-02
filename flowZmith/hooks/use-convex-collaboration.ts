import { useQuery, useMutation } from "convex/react";
import { api } from "../convex/_generated/api";
import { Id } from "../convex/_generated/dataModel";

// Hook for starting a collaboration session
export function useStartCollaborationSession() {
  return useMutation(api.collaboration.startCollaborationSession);
}

// Hook for joining a collaboration session
export function useJoinCollaborationSession() {
  return useMutation(api.collaboration.joinCollaborationSession);
}

// Hook for leaving a collaboration session
export function useLeaveCollaborationSession() {
  return useMutation(api.collaboration.leaveCollaborationSession);
}

// Hook for updating cursor position
export function useUpdateCursorPosition() {
  return useMutation(api.collaboration.updateCursorPosition);
}

// Hook for applying code changes
export function useApplyCodeChange() {
  return useMutation(api.collaboration.applyCodeChange);
}

// Hook for getting active session
export function useActiveSession(contractId: Id<"contracts"> | undefined) {
  return useQuery(
    api.collaboration.getActiveSession,
    contractId ? { contractId } : "skip"
  );
}

// Hook for getting recent changes
export function useRecentChanges(
  sessionId: Id<"collaborationSessions"> | undefined,
  limit?: number
) {
  return useQuery(
    api.collaboration.getRecentChanges,
    sessionId ? { sessionId, limit } : "skip"
  );
}

// Hook for getting collaboration statistics
export function useCollaborationStats(contractId: Id<"contracts"> | undefined) {
  return useQuery(
    api.collaboration.getCollaborationStats,
    contractId ? { contractId } : "skip"
  );
}

// Hook for cleaning up inactive sessions
export function useCleanupInactiveSessions() {
  return useMutation(api.collaboration.cleanupInactiveSessions);
}