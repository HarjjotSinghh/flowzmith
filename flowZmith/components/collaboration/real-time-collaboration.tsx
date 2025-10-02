"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  useActiveSession,
  useStartCollaborationSession,
  useJoinCollaborationSession,
  useLeaveCollaborationSession,
  useRecentChanges,
  useCollaborationStats
} from "@/hooks/use-convex-collaboration";
import { Id } from "@/convex/_generated/dataModel";
import { 
  Users, 
  UserPlus, 
  UserMinus, 
  Activity, 
  Clock,
  Code,
  Eye,
  Edit
} from "lucide-react";

interface RealTimeCollaborationProps {
  contractId: Id<"contracts">;
  currentUserId?: string;
}

export function RealTimeCollaboration({ 
  contractId, 
  currentUserId 
}: RealTimeCollaborationProps) {
  const [isJoining, setIsJoining] = useState(false);
  const [cursorPosition, setCursorPosition] = useState({ line: 0, column: 0 });

  const activeSession = useActiveSession(contractId);
  const recentChanges = useRecentChanges(activeSession?._id, 20);
  const collaborationStats = useCollaborationStats(contractId);
  
  const startSession = useStartCollaborationSession();
  const joinSession = useJoinCollaborationSession();
  const leaveSession = useLeaveCollaborationSession();

  const handleStartSession = async () => {
    if (!currentUserId) return;
    
    try {
      setIsJoining(true);
      await startSession({
        contractId
      });
    } catch (error) {
      console.error("Failed to start collaboration session:", error);
    } finally {
      setIsJoining(false);
    }
  };

  const handleJoinSession = async () => {
    if (!currentUserId || !activeSession) return;
    
    try {
      setIsJoining(true);
      await joinSession({
        sessionId: activeSession._id
      });
    } catch (error) {
      console.error("Failed to join collaboration session:", error);
    } finally {
      setIsJoining(false);
    }
  };

  const handleLeaveSession = async () => {
    if (!currentUserId || !activeSession) return;
    
    try {
      await leaveSession({
        sessionId: activeSession._id
      });
    } catch (error) {
      console.error("Failed to leave collaboration session:", error);
    }
  };

  const isUserInSession = activeSession?.participants?.some(
    (p: any) => p.userId === currentUserId
  );

  const getChangeTypeIcon = (type: string) => {
    switch (type) {
      case "insert":
        return <Edit className="h-4 w-4 text-green-500" />;
      case "delete":
        return <UserMinus className="h-4 w-4 text-red-500" />;
      case "modify":
        return <Code className="h-4 w-4 text-blue-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Session Status */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Collaboration Session
              {activeSession && (
                <Badge variant="secondary" className="bg-green-100 text-green-800">
                  Active
                </Badge>
              )}
            </CardTitle>
            <div className="flex items-center gap-2">
              {!activeSession ? (
                <Button
                  onClick={handleStartSession}
                  disabled={isJoining}
                  className="flex items-center gap-2"
                >
                  <UserPlus className="h-4 w-4" />
                  Start Session
                </Button>
              ) : !isUserInSession ? (
                <Button
                  onClick={handleJoinSession}
                  disabled={isJoining}
                  variant="outline"
                  className="flex items-center gap-2"
                >
                  <UserPlus className="h-4 w-4" />
                  Join Session
                </Button>
              ) : (
                <Button
                  onClick={handleLeaveSession}
                  variant="destructive"
                  className="flex items-center gap-2"
                >
                  <UserMinus className="h-4 w-4" />
                  Leave Session
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        {activeSession && (
          <CardContent>
            <div className="space-y-4">
              {/* Active Participants */}
              <div>
                <h4 className="font-medium text-sm mb-3 flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  Active Participants ({activeSession.participants?.length || 0})
                </h4>
                <div className="flex flex-wrap gap-2">
                  {activeSession.participants?.map((participant: any) => (
                    <div
                      key={participant.userId}
                      className="flex items-center gap-2 p-2 border rounded-lg bg-accent/50"
                    >
                      <Avatar className="h-6 w-6">
                        <AvatarImage src={participant.userAvatar} />
                        <AvatarFallback className="text-xs">
                          {participant.userName?.charAt(0) || "U"}
                        </AvatarFallback>
                      </Avatar>
                      <span className="text-sm font-medium">
                        {participant.userName}
                      </span>
                      <div className="flex items-center gap-1">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                        <span className="text-xs text-muted-foreground">
                          {participant.role || "collaborator"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Session Stats */}
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="p-3 border rounded-lg">
                  <p className="text-lg font-bold text-blue-600">
                    {collaborationStats?.totalSessions || 0}
                  </p>
                  <p className="text-xs text-muted-foreground">Total Sessions</p>
                </div>
                <div className="p-3 border rounded-lg">
                  <p className="text-lg font-bold text-green-600">
                    {collaborationStats?.totalChanges || 0}
                  </p>
                  <p className="text-xs text-muted-foreground">Total Changes</p>
                </div>
                <div className="p-3 border rounded-lg">
                  <p className="text-lg font-bold text-purple-600">
                    {collaborationStats?.uniqueCollaborators || 0}
                  </p>
                  <p className="text-xs text-muted-foreground">Collaborators</p>
                </div>
              </div>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Recent Changes */}
      {activeSession && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Recent Changes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-64">
              <div className="space-y-3">
                {recentChanges?.map((change: any) => (
                  <div
                    key={change._id}
                    className="flex items-start gap-3 p-3 border rounded-lg hover:bg-accent/50 transition-colors"
                  >
                    {getChangeTypeIcon(change.type)}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-sm">
                          {change.userName}
                        </span>
                        <Badge variant="outline" className="text-xs">
                          {change.type}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-1">
                        Line {change.startLine}-{change.endLine}
                      </p>
                      {change.content && (
                        <pre className="text-xs bg-muted p-2 rounded border overflow-x-auto">
                          {change.content.slice(0, 100)}
                          {change.content.length > 100 && "..."}
                        </pre>
                      )}
                      <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        {new Date(change._creationTime).toLocaleString()}
                      </div>
                    </div>
                  </div>
                ))}
                {(!recentChanges || recentChanges.length === 0) && (
                  <div className="text-center py-8">
                    <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">
                      No recent changes in this session
                    </p>
                  </div>
                )}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}
    </div>
  );
}