/**
 * Toast Notification Utility (TypeScript version)
 */
import type { ToastOptions } from '@types/portfolio';

export class ToastManager {
  private container: HTMLElement | null = null;

  constructor() {
    this.initContainer();
  }

  private initContainer(): void {
    // Create toast container if it doesn't exist
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    this.container = container;
  }

  show(message: string, options: ToastOptions = {}): void {
    if (!this.container) this.initContainer();

    const {
      type = 'info',
      duration = 3000,
      position = 'top-right'
    } = options;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type} toast-${position}`;
    toast.innerHTML = `
      <div class="toast-content">
        <span class="toast-icon">${this.getIcon(type)}</span>
        <span class="toast-message">${message}</span>
      </div>
    `;

    this.container?.appendChild(toast);

    // Animate in
    setTimeout(() => toast.classList.add('show'), 10);

    // Remove after duration
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }

  private getIcon(type: string): string {
    const icons: Record<string, string> = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ℹ'
    };
    return icons[type] || icons.info;
  }

  success(message: string, duration?: number): void {
    this.show(message, { type: 'success', duration });
  }

  error(message: string, duration?: number): void {
    this.show(message, { type: 'error', duration });
  }

  warning(message: string, duration?: number): void {
    this.show(message, { type: 'warning', duration });
  }

  info(message: string, duration?: number): void {
    this.show(message, { type: 'info', duration });
  }
}

// Export singleton instance
export const toast = new ToastManager();
export default toast;
