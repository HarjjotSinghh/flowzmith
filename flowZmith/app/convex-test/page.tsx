"use client";

import React from "react";
import { RealTimeDashboard } from "@/components/analytics/real-time-dashboard";
import { RealTimeNotifications } from "@/components/notifications/real-time-notifications";
import { RealTimeCollaboration } from "@/components/collaboration/real-time-collaboration";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useCreateContract, useUserContracts } from "@/hooks/use-convex-contracts";
import { useCreateNotification } from "@/hooks/use-convex-notifications";
import { Badge } from "@/components/ui/badge";
import { Database, Zap, Users, Bell } from "lucide-react";

export default function ConvexTestPage() {
  const userContracts = useUserContracts(10);
  const createContract = useCreateContract();
  const createNotification = useCreateNotification();

  const handleCreateTestContract = async () => {
    try {
      await createContract({
        name: `Test Contract ${Date.now()}`,
        description: "A test smart contract created to demonstrate Convex integration",
        code: `// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TestContract {
    string public message;
    
    constructor(string memory _message) {
        message = _message;
    }
    
    function updateMessage(string memory _newMessage) public {
        message = _newMessage;
    }
}`,
        language: "solidity",
        network: "ethereum",
        tags: ["test", "demo"],
        isPublic: true
      });
    } catch (error) {
      console.error("Failed to create test contract:", error);
    }
  };

  const handleCreateTestNotification = async () => {
    try {
      await createNotification({
        userId: "user_test123" as any,
        type: "system_update",
        title: "Test Notification",
        message: "This is a test notification to demonstrate real-time updates"
      });
    } catch (error) {
      console.error("Failed to create test notification:", error);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold flex items-center justify-center gap-3">
          <Database className="h-10 w-10 text-blue-600" />
          Convex Integration Test
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          This page demonstrates the real-time capabilities of Convex integration 
          with smart contract management, collaboration, and notifications.
        </p>
        <div className="flex items-center justify-center gap-2">
          <Badge variant="secondary" className="bg-green-100 text-green-800">
            <Zap className="h-3 w-3 mr-1" />
            Real-time Updates
          </Badge>
          <Badge variant="secondary" className="bg-blue-100 text-blue-800">
            <Users className="h-3 w-3 mr-1" />
            Collaboration
          </Badge>
          <Badge variant="secondary" className="bg-purple-100 text-purple-800">
            <Bell className="h-3 w-3 mr-1" />
            Notifications
          </Badge>
        </div>
      </div>

      {/* Test Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Test Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <Button onClick={handleCreateTestContract} className="flex items-center gap-2">
              <Database className="h-4 w-4" />
              Create Test Contract
            </Button>
            <Button onClick={handleCreateTestNotification} variant="outline" className="flex items-center gap-2">
              <Bell className="h-4 w-4" />
              Create Test Notification
            </Button>
          </div>
          <div className="mt-4 p-4 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground">
              <strong>Current Contracts:</strong> {userContracts?.length || 0} contracts loaded
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Real-time Dashboard */}
      <div>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Zap className="h-6 w-6" />
          Real-time Analytics Dashboard
        </h2>
        <RealTimeDashboard />
      </div>

      {/* Notifications */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Bell className="h-6 w-6" />
            Real-time Notifications
          </h2>
          <RealTimeNotifications />
        </div>

        {/* Collaboration */}
        <div>
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Users className="h-6 w-6" />
            Real-time Collaboration
          </h2>
          {userContracts && userContracts.length > 0 ? (
            <RealTimeCollaboration 
              contractId={userContracts[0]._id} 
              currentUserId="test-user"
            />
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <p className="text-muted-foreground">
                  Create a contract first to test collaboration features
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Integration Status */}
      <Card>
        <CardHeader>
          <CardTitle>Integration Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center gap-3 p-4 border rounded-lg">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <div>
                <p className="font-medium">Convex Backend</p>
                <p className="text-sm text-muted-foreground">Connected & Running</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-4 border rounded-lg">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <div>
                <p className="font-medium">Real-time Updates</p>
                <p className="text-sm text-muted-foreground">Active</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-4 border rounded-lg">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <div>
                <p className="font-medium">Authentication</p>
                <p className="text-sm text-muted-foreground">Ready</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}