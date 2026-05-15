import React from 'react';
import { getPrediction } from '../services/api';

interface PredictionResult {
  prediction: number;
  confidence: number;
  timestamp: string;
}

const PredictionDashboard: React.FC<{ ticker: string; date: string; metric: string }> = ({
  ticker,
  date,
  metric,
}) => {
  const [prediction, setPrediction] = React.useState<number | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const loadPrediction = async () => {
      try {
        const result = await getPrediction(ticker, date, metric);
        setPrediction(result.prediction);
        setError(null);
      } catch (err: any) {
        const message = err?.response?.data?.detail || err?.message || 'Failed to get prediction';
        console.error('Prediction fetch error:', err);
        setError(`Failed to get prediction: ${message}`);
        setPrediction(null);
      } finally {
        setLoading(false);
      }
    };
    loadPrediction();
  }, [ticker, date, metric]);

  if (loading) return <div>Loading prediction...</div>;
  if (error) return <div className="error">❌ {error}</div>;

  return (
    <div className="prediction-card">
      <h3>Earnings Prediction</h3>
      <div className="prediction-value">
        {prediction !== null ? <strong>${prediction.toFixed(2)}</strong> : 'N/A'}
      </div>
      <div className="confidence">Confidence: 80%</div>
    </div>
  );
};

export default PredictionDashboard;
