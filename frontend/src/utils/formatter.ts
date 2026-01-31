/**
 * Formatting Utilities
 */

export class Formatter {
  /**
   * Format currency in Indian Rupees
   */
  static currency(amount: number, decimals: number = 0): string {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: decimals
    }).format(amount);
  }

  /**
   * Format number with Indian number system (Lakhs/Crores)
   */
  static numberIndian(num: number): string {
    if (num >= 10000000) {
      return `₹${(num / 10000000).toFixed(2)} Cr`;
    } else if (num >= 100000) {
      return `₹${(num / 100000).toFixed(2)} L`;
    } else if (num >= 1000) {
      return `₹${(num / 1000).toFixed(2)} K`;
    }
    return `₹${num.toFixed(0)}`;
  }

  /**
   * Format percentage
   */
  static percentage(value: number, decimals: number = 2): string {
    return `${value.toFixed(decimals)}%`;
  }

  /**
   * Format date to readable string
   */
  static date(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }

  /**
   * Format relative time (e.g., "2 hours ago")
   */
  static relativeTime(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`;
    
    return this.date(dateString);
  }

  /**
   * Truncate text with ellipsis
   */
  static truncate(text: string, maxLength: number): string {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3) + '...';
  }

  /**
   * Format return percentage with color class
   */
  static returnWithClass(returnPct: number): { text: string; className: string } {
    const text = this.percentage(returnPct);
    const className = returnPct >= 0 ? 'text-success' : 'text-danger';
    return { text, className };
  }
}

export default Formatter;
