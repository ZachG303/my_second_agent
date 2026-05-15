import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || '/api';

export const fetchReports = async (limit = 10) => {
  const response = await axios.get(`${API_BASE}/scrape/reports`, {
    params: { limit },
  });
  return response.data;
};

export const fetchInflectionInsights = async (tickers?: string) => {
  const query = tickers ? `?tickers=${encodeURIComponent(tickers)}` : '';
  const response = await axios.get(`${API_BASE}/analysis/inflection${query}`);
  return response.data;
};

export const trainModel = async (period: string, metric: string) => {
  const response = await axios.post(`${API_BASE}/train/model`, {
    period,
    metric,
  });
  return response.data;
};

export const getPrediction = async (ticker: string, date: string, metric: string) => {
  const response = await axios.get(`${API_BASE}/predict`, {
    params: { ticker, date, metric },
  });
  return response.data;
};
