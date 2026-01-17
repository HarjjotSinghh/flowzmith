"use client";

import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  useUserNotifications, 
  useMarkNotificationAsRead, 
  useMarkAllNotificationsAsRead,
  useDeleteNotification 
} from "@/hooks/use-convex-notifications";
import { 
  Bell, 
  Check, 
  CheckCheck, 
  X, 
  AlertCircle, 
  Info, 
  CheckCircle,
  XCircle,
  Users
} from "lucide-react";

export function RealTimeNotifications() {
  const [showUnreadOnly, setShowUnreadOnly] = useState(false);
  const notifications = useUserNotifications(50, showUnreadOnly);
  const markAsRead = useMarkNotificationAsRead();
  const markAllAsRead = useMarkAllNotificationsAsRead();
  const deleteNotification = useDeleteNotification();

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "deployment_success":
        return <CheckCircle className="h-4 w-4 text-primary" />;
      case "deployment_failed":
        return <XCircle className="h-4 w-4 text-destructive" />;
      case "collaboration_invite":
        return <Users className="h-4 w-4 text-foreground/80" />;
      case "system":
        return <AlertCircle className="h-4 w-4 text-orange-500" />;
      default:
        return <Info className="h-4 w-4 text-foreground/80" />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case "deployment_success":
        return "border-l-primary";
      case "deployment_failed":
        return "border-l-destructive";
      case "collaboration_invite":
        return "border-l-border";
      case "system":
        return "border-l-orange-500";
      default:
        return "border-l-gray-500";
    }
  };

  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await markAsRead({ notificationId: notificationId as any });
    } catch (error) {
      console.error("Failed to mark notification as read:", error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await markAllAsRead({});
    } catch (error) {
      console.error("Failed to mark all notifications as read:", error);
    }
  };

  const handleDeleteNotification = async (notificationId: string) => {
    try {
      await deleteNotification({ notificationId: notificationId as any });
    } catch (error) {
      console.error("Failed to delete notification:", error);
    }
  };

  const unreadCount = notifications?.filter((n: any) => !n.read).length || 0;

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Notifications
            {unreadCount > 0 && (
              <Badge variant="destructive" className="ml-2">
                {unreadCount}
              </Badge>
            )}
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowUnreadOnly(!showUnreadOnly)}
            >
              {showUnreadOnly ? "Show All" : "Unread Only"}
            </Button>
            {unreadCount > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleMarkAllAsRead}
                className="flex items-center gap-1"
              >
                <CheckCheck className="h-4 w-4" />
                Mark All Read
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-96">
          <div className="space-y-3">
            {notifications?.map((notification: any) => (
              <div
                key={notification._id}
                className={`p-4 border-l-4 rounded-lg bg-card hover:bg-accent/50 transition-colors ${
                  getNotificationColor(notification.type)
                } ${!notification.read ? "bg-accent/20" : ""}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    {getNotificationIcon(notification.type)}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium text-sm">
                          {notification.title}
                        </h4>
                        {!notification.read && (
                          <div className="w-2 h-2 bg-primary rounded-full" />
                        )}
                      </div>
                      <p className="text-sm text-foreground/80 mb-2">
                        {notification.message}
                      </p>
                      <div className="flex items-center gap-4 text-xs text-foreground/80">
                        <span>
                          {new Date(notification._creationTime).toLocaleString()}
                        </span>
                        <Badge variant="outline" className="text-xs">
                          {notification.type.replace("_", " ")}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 ml-2">
                    {!notification.read && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleMarkAsRead(notification._id)}
                        className="h-8 w-8 p-0"
                      >
                        <Check className="h-4 w-4" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteNotification(notification._id)}
                      className="h-8 w-8 p-0 text-foreground/80 hover:text-destructive"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
            {(!notifications || notifications.length === 0) && (
              <div className="text-center py-8">
                <Bell className="h-12 w-12 text-foreground/80 mx-auto mb-4" />
                <p className="text-foreground/80">
                  {showUnreadOnly ? "No unread notifications" : "No notifications yet"}
                </p>
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
