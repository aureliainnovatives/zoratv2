import { Component, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NotificationService, Notification } from '../../services/notification.service';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [CommonModule, TranslatePipe],
  templateUrl: './notifications.component.html'
})
export class NotificationsComponent {
  notifications = computed(() => this.notificationService.getNotifications());
  protected readonly Date = Date;

  constructor(private notificationService: NotificationService) {}

  getIcon(type: Notification['type']): string {
    switch (type) {
      case 'success':
        return `
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
        `;
      case 'error':
        return `
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        `;
      case 'warning':
        return `
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
          </svg>
        `;
      case 'info':
      default:
        return `
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        `;
    }
  }

  getProgressBarColor(type: Notification['type']): string {
    switch (type) {
      case 'success':
        return 'bg-success';
      case 'error':
        return 'bg-error';
      case 'warning':
        return 'bg-warning';
      case 'info':
      default:
        return 'bg-primary';
    }
  }

  getBackgroundColor(type: Notification['type']): string {
    switch (type) {
      case 'success':
        return 'bg-success/10 border-success/20';
      case 'error':
        return 'bg-error/10 border-error/20';
      case 'warning':
        return 'bg-warning/10 border-warning/20';
      case 'info':
      default:
        return 'bg-primary/10 border-primary/20';
    }
  }

  getTextColor(type: Notification['type']): string {
    switch (type) {
      case 'success':
        return 'text-success';
      case 'error':
        return 'text-error';
      case 'warning':
        return 'text-warning';
      case 'info':
      default:
        return 'text-primary';
    }
  }

  close(id: string): void {
    this.notificationService.remove(id);
  }
} 