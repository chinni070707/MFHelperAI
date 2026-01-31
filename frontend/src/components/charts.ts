/**
 * Chart Components using Chart.js and Plotly
 */
import Chart from 'chart.js/auto';
import Plotly from 'plotly.js-dist';
import type { ChartConfig } from '@types/portfolio';

export class ChartManager {
  private charts: Map<string, Chart | any> = new Map();

  /**
   * Create a Chart.js chart
   */
  createChart(elementId: string, config: ChartConfig): Chart | null {
    const canvas = document.getElementById(elementId) as HTMLCanvasElement;
    if (!canvas) {
      console.error(`Canvas element not found: ${elementId}`);
      return null;
    }

    // Destroy existing chart
    this.destroyChart(elementId);

    const chart = new Chart(canvas, config as any);
    this.charts.set(elementId, chart);
    return chart;
  }

  /**
   * Create a Plotly chart
   */
  createPlotlyChart(elementId: string, data: any[], layout: any = {}, config: any = {}): void {
    const element = document.getElementById(elementId);
    if (!element) {
      console.error(`Element not found: ${elementId}`);
      return;
    }

    // Destroy existing chart
    this.destroyChart(elementId);

    Plotly.newPlot(elementId, data, layout, {
      responsive: true,
      displayModeBar: false,
      ...config
    });

    this.charts.set(elementId, { type: 'plotly' });
  }

  /**
   * Create pie chart
   */
  createPieChart(elementId: string, labels: string[], values: number[], colors?: string[]): Chart | null {
    return this.createChart(elementId, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: colors || this.getDefaultColors(values.length),
          borderWidth: 2,
          borderColor: '#fff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 15,
              font: { size: 12 }
            }
          },
          tooltip: {
            callbacks: {
              label: (context: any) => {
                const label = context.label || '';
                const value = context.parsed || 0;
                const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
                const percentage = ((value / total) * 100).toFixed(1);
                return `${label}: ${percentage}%`;
              }
            }
          }
        }
      }
    });
  }

  /**
   * Create bar chart
   */
  createBarChart(elementId: string, labels: string[], values: number[], title?: string): Chart | null {
    return this.createChart(elementId, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: title || 'Value',
          data: values,
          backgroundColor: 'rgba(59, 130, 246, 0.8)',
          borderColor: 'rgba(59, 130, 246, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: (value: any) => {
                if (value >= 1000000) return `₹${(value / 1000000).toFixed(1)}M`;
                if (value >= 1000) return `₹${(value / 1000).toFixed(0)}K`;
                return `₹${value}`;
              }
            }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }

  /**
   * Create treemap using Plotly
   */
  createTreemap(elementId: string, labels: string[], parents: string[], values: number[]): void {
    const data = [{
      type: 'treemap',
      labels,
      parents,
      values,
      textposition: 'middle center',
      marker: {
        colors: values,
        colorscale: 'Blues',
        showscale: false
      }
    }];

    const layout = {
      margin: { t: 10, l: 10, r: 10, b: 10 },
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent'
    };

    this.createPlotlyChart(elementId, data, layout);
  }

  /**
   * Destroy chart
   */
  destroyChart(elementId: string): void {
    const chart = this.charts.get(elementId);
    if (chart) {
      if (chart.destroy) {
        chart.destroy();
      } else if (chart.type === 'plotly') {
        Plotly.purge(elementId);
      }
      this.charts.delete(elementId);
    }
  }

  /**
   * Destroy all charts
   */
  destroyAll(): void {
    this.charts.forEach((_, key) => this.destroyChart(key));
  }

  /**
   * Get default color palette
   */
  private getDefaultColors(count: number): string[] {
    const colors = [
      '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
      '#EC4899', '#14B8A6', '#F97316', '#6366F1', '#84CC16'
    ];
    return colors.slice(0, count);
  }
}

// Export singleton instance
export const chartManager = new ChartManager();
export default chartManager;
