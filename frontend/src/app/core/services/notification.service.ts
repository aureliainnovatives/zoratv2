import { Injectable, signal } from '@angular/core';
import { environment } from '../../../environments/environment';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  title?: string;
  duration?: number;
  showProgressBar?: boolean;
  createdAt: number;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private notifications = signal<Notification[]>([]);

  constructor() {
    // Clean up expired notifications periodically
    setInterval(() => this.cleanupExpiredNotifications(), 1000);
  }

  success(message: string, title?: string, duration?: number): void {
    this.show({
      type: 'success',
      message,
      title,
      duration
    });
  }

  error(message: string, title?: string, duration?: number): void {
    this.show({
      type: 'error',
      message,
      title,
      duration
    });
  }

  warning(message: string, title?: string, duration?: number): void {
    this.show({
      type: 'warning',
      message,
      title,
      duration
    });
  }

  info(message: string, title?: string, duration?: number): void {
    this.show({
      type: 'info',
      message,
      title,
      duration
    });
  }

  private show(notification: Partial<Notification>): void {
    const id = this.generateId();
    const now = Date.now();

    const fullNotification: Notification = {
      id,
      type: notification.type || 'info',
      message: notification.message || '',
      title: notification.title,
      duration: notification.duration || environment.notifications.duration,
      showProgressBar: notification.showProgressBar ?? environment.notifications.showProgressBar,
      createdAt: now
    };

    this.notifications.update(notifications => [...notifications, fullNotification]);

    // Remove notification after duration
    if (fullNotification.duration !== Infinity) {
      setTimeout(() => {
        this.remove(id);
      }, fullNotification.duration);
    }
  }

  remove(id: string): void {
    this.notifications.update(notifications => 
      notifications.filter(notification => notification.id !== id)
    );
  }

  clear(): void {
    this.notifications.set([]);
  }

  getNotifications(): Notification[] {
    return this.notifications();
  }

  private generateId(): string {
    return Math.random().toString(36).substring(2, 15);
  }

  private cleanupExpiredNotifications(): void {
    const now = Date.now();
    this.notifications.update(notifications =>
      notifications.filter(notification => {
        const expiryTime = notification.createdAt + notification.duration!;
        return expiryTime > now || notification.duration === Infinity;
      })
    );
  }
} 