import { useQuery, useMutation } from "convex/react";
import { api } from "../convex/_generated/api";
import { Id } from "../convex/_generated/dataModel";

// Hook for getting user notifications
export function useUserNotifications(limit?: number, unreadOnly?: boolean) {
  return useQuery(api.notifications.getUserNotifications, {
    limit,
    unreadOnly,
  });
}

// Hook for marking notification as read
export function useMarkNotificationAsRead() {
  return useMutation(api.notifications.markNotificationAsRead);
}

// Hook for marking all notifications as read
export function useMarkAllNotificationsAsRead() {
  return useMutation(api.notifications.markAllNotificationsAsRead);
}

// Hook for creating a notification
export function useCreateNotification() {
  return useMutation(api.notifications.createNotification);
}

// Hook for deleting a notification
export function useDeleteNotification() {
  return useMutation(api.notifications.deleteNotification);
}

// Hook for getting unread notification count
export function useUnreadNotificationCount() {
  return useQuery(api.notifications.getUnreadNotificationCount);
}

// Hook for sending system notification
export function useSendSystemNotification() {
  return useMutation(api.notifications.sendSystemNotification);
}