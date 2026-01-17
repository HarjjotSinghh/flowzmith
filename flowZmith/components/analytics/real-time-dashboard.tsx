"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useDeploymentStats, useRecentDeploymentActivity } from "@/hooks/use-convex-deployments";
import { useUserContracts } from "@/hooks/use-convex-contracts";
import { useUnreadNotificationCount } from "@/hooks/use-convex-notifications";
import { 
  Activity, 
  TrendingUp, 
  Users, 
  FileText, 
  Bell,
  CheckCircle,
  XCircle,
  Clock
} from "lucide-react";

export function RealTimeDashboard() {
  const deploymentStats = useDeploymentStats("7d");
  const recentActivity = useRecentDeploymentActivity(10);
  const userContracts = useUserContracts(50);
  const unreadCount = useUnreadNotificationCount();

  const getStatusColor = (status: string) => {
    switch (status) {
      case "success":
        return "bg-primary";
      case "failed":
        return "bg-destructive";
      case "pending":
        return "bg-muted-foreground";
      default:
        return "bg-muted-foreground";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircle className="h-4 w-4 text-primary" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-destructive" />;
      case "pending":
        return <Clock className="h-4 w-4 text-foreground/80" />;
      default:
        return <Activity className="h-4 w-4 text-foreground/80" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Contracts</CardTitle>
            <FileText className="h-4 w-4 text-foreground/80" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {userContracts?.length || 0}
            </div>
            <p className="text-xs text-foreground/80">
              Active smart contracts
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Deployments (7d)</CardTitle>
            <TrendingUp className="h-4 w-4 text-foreground/80" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {deploymentStats?.totalDeployments || 0}
            </div>
            <p className="text-xs text-foreground/80">
              {deploymentStats?.successRate || 0}% success rate
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Deployments</CardTitle>
            <Users className="h-4 w-4 text-foreground/80" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {deploymentStats?.pendingDeployments || 0}
            </div>
            <p className="text-xs text-foreground/80">
              Pending deployments
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Notifications</CardTitle>
            <Bell className="h-4 w-4 text-foreground/80" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {unreadCount || 0}
            </div>
            <p className="text-xs text-foreground/80">
              Unread notifications
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Recent Deployments
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity?.map((deployment: any) => (
                <div
                  key={deployment._id}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    {getStatusIcon(deployment.status)}
                    <div>
                      <p className="font-medium text-sm">
                        {deployment.contractName}
                      </p>
                      <p className="text-xs text-foreground/80">
                        {deployment.network} • {new Date(deployment._creationTime).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <Badge
                    variant="secondary"
                    className={`${getStatusColor(deployment.status)} text-white`}
                  >
                    {deployment.status}
                  </Badge>
                </div>
              ))}
              {(!recentActivity || recentActivity.length === 0) && (
                <p className="text-sm text-foreground/80 text-center py-4">
                  No recent deployments
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Deployment Success Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Success Rate</span>
                  <span>{deploymentStats?.successRate || 0}%</span>
                </div>
                <Progress value={deploymentStats?.successRate || 0} className="h-2" />
              </div>
              
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-primary">
                    {deploymentStats?.successfulDeployments || 0}
                  </p>
                  <p className="text-xs text-foreground/80">Successful</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-destructive">
                    {deploymentStats?.failedDeployments || 0}
                  </p>
                  <p className="text-xs text-foreground/80">Failed</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-foreground">
                    {deploymentStats?.pendingDeployments || 0}
                  </p>
                  <p className="text-xs text-foreground/80">Pending</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Contract Status Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Contract Overview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {userContracts?.slice(0, 6).map((contract: any) => (
              <div
                key={contract._id}
                className="p-4 border rounded-lg hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-sm truncate">
                    {contract.name}
                  </h4>
                  <Badge variant="outline" className="text-xs">
                    {contract.language}
                  </Badge>
                </div>
                <p className="text-xs text-foreground/80 mb-2">
                  {contract.description?.slice(0, 80)}...
                </p>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-foreground/80">
                    {new Date(contract._creationTime).toLocaleDateString()}
                  </span>
                  <Badge
                    variant="secondary"
                    className={`${getStatusColor(contract.status)} text-white`}
                  >
                    {contract.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
