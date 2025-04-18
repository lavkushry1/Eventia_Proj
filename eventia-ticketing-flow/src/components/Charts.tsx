// Charts.tsx
import React from 'react';
import { Bar, Line, Doughnut, Scatter } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
  ArcElement,
  RadialLinearScale,
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend
);

interface ChartData {
  labels: string[];
  values: number[];
}

interface ChartProps {
  data: ChartData;
  title?: string;
  color?: string;
  height?: number;
}

// Default chart options
const defaultOptions: ChartOptions<'bar' | 'line'> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      padding: 12,
      titleFont: {
        size: 14,
      },
      bodyFont: {
        size: 13,
      },
      displayColors: false,
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(0, 0, 0, 0.05)',
      },
      ticks: {
        padding: 10,
      }
    },
    x: {
      grid: {
        display: false,
      },
      ticks: {
        padding: 10,
      }
    }
  }
};

export const BarChart: React.FC<ChartProps> = ({ 
  data, 
  title = '', 
  color = 'rgba(99, 102, 241, 0.8)',
  height = 300
}) => {
  const chartData = {
    labels: data.labels,
    datasets: [
      {
        label: title,
        data: data.values,
        backgroundColor: color,
        borderRadius: 4,
        maxBarThickness: 40,
      },
    ],
  };

  const options = {
    ...defaultOptions,
    plugins: {
      ...defaultOptions.plugins,
      title: {
        display: !!title,
        text: title,
        font: {
          size: 16,
        },
      },
    },
  };

  return (
    <div style={{ height: height }}>
      <Bar data={chartData} options={options} />
    </div>
  );
};

export const LineChart: React.FC<ChartProps> = ({ 
  data, 
  title = '', 
  color = 'rgba(16, 185, 129, 0.8)',
  height = 300
}) => {
  const chartData = {
    labels: data.labels,
    datasets: [
      {
        label: title,
        data: data.values,
        borderColor: color,
        backgroundColor: `${color.slice(0, -4)}0.1)`,
        tension: 0.3,
        fill: true,
        pointBackgroundColor: color,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
    ],
  };

  const options = {
    ...defaultOptions,
    plugins: {
      ...defaultOptions.plugins,
      title: {
        display: !!title,
        text: title,
        font: {
          size: 16,
        },
      },
    },
  };

  return (
    <div style={{ height: height }}>
      <Line data={chartData} options={options} />
    </div>
  );
};

export const DoughnutChart: React.FC<ChartProps> = ({
  data,
  title = '',
  height = 300,
}) => {
  // Create a color array for the doughnut segments
  const backgroundColors = [
    'rgba(99, 102, 241, 0.8)',   // Indigo
    'rgba(16, 185, 129, 0.8)',   // Emerald
    'rgba(245, 158, 11, 0.8)',   // Amber
    'rgba(239, 68, 68, 0.8)',    // Red
    'rgba(59, 130, 246, 0.8)',   // Blue
    'rgba(217, 70, 239, 0.8)',   // Fuchsia
    'rgba(20, 184, 166, 0.8)',   // Teal
  ];

  const chartData = {
    labels: data.labels,
    datasets: [
      {
        data: data.values,
        backgroundColor: data.labels.map((_, i) => backgroundColors[i % backgroundColors.length]),
        borderWidth: 1,
        borderColor: '#ffffff',
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
        labels: {
          padding: 20,
          boxWidth: 12,
          font: {
            size: 12,
          },
        },
      },
      title: {
        display: !!title,
        text: title,
        font: {
          size: 16,
        },
        padding: {
          bottom: 20,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: {
          size: 14,
        },
        bodyFont: {
          size: 13,
        },
        callbacks: {
          label: function(context: {
            chart: { data: { datasets: Array<{ data: number[] }> } };
            label?: string;
            raw?: number;
          }) {
            const label = context.label || '';
            const value = context.raw || 0;
            const total = context.chart.data.datasets[0].data.reduce((a: number, b: number) => a + b, 0);
            const percentage = Math.round((value / total) * 100);
            return `${label}: ${value} (${percentage}%)`;
          }
        }
      },
    },
    cutout: '65%',
  };

  return (
    <div style={{ height: height }}>
      <Doughnut data={chartData} options={options} />
    </div>
  );
};

export const HorizontalBarChart: React.FC<ChartProps> = ({
  data,
  title = '',
  color = 'rgba(99, 102, 241, 0.8)',
  height = 300
}) => {
  const chartData = {
    labels: data.labels,
    datasets: [
      {
        label: title,
        data: data.values,
        backgroundColor: color,
        borderRadius: 4,
        maxBarThickness: 30,
      },
    ],
  };

  const options = {
    indexAxis: 'y' as const,
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: !!title,
        text: title,
        font: {
          size: 16,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: {
          size: 14,
        },
        bodyFont: {
          size: 13,
        },
        displayColors: false,
      },
    },
    scales: {
      x: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
        ticks: {
          padding: 10,
        }
      },
      y: {
        grid: {
          display: false,
        },
        ticks: {
          padding: 10,
        }
      }
    }
  };

  return (
    <div style={{ height: height }}>
      <Bar data={chartData} options={options} />
    </div>
  );
};

// Other chart types can be added as needed
