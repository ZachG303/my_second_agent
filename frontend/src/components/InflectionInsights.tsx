import React from 'react';
import { fetchInflectionInsights } from '../services/api';

interface InflectionInsight {
  company_ticker: string;
  latest_filing_date: string | null;
  price: number;
  sales_multiple: number | null;
  peg: number | null;
  narrative_shift: boolean;
  cheap_on_sales: boolean;
  multi_theme_exposure: boolean;
  ecosystem_halo: boolean;
  peg_value: boolean;
  technical_confirmed: boolean;
  score: number;
  theme_tags: string[];
  highlights: string[];
  latest_filings: string[];
  summary: string;
}

const defaultTickers = 'AMKR,PLAB,ENS,PLPC,VIAV,MITK,SYNA,OSS,VPG,FIVN';

const InflectionInsights: React.FC = () => {
  const [insights, setInsights] = React.useState<InflectionInsight[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const loadInsights = async () => {
      try {
        const data = await fetchInflectionInsights(defaultTickers);
        setInsights(data);
      } catch (err: any) {
        console.error('Failed to fetch inflection insights:', err);
        setError(err?.response?.data?.detail || err?.message || 'Unable to load insights');
      } finally {
        setLoading(false);
      }
    };

    loadInsights();
  }, []);

  if (loading) return <div>Loading inflection analysis...</div>;
  if (error) return <div className="error">❌ {error}</div>;

  return (
    <div className="inflection-insights">
      <h2>Inflection Point Insights</h2>
      {insights.length === 0 ? (
        <p>No insights available right now.</p>
      ) : (
        insights.map((insight) => (
          <div key={insight.company_ticker} className="insight-card">
            <h3>{insight.company_ticker}</h3>
            <p>{insight.summary}</p>
            <div className="insight-grid">
              <div>Latest filing: {insight.latest_filing_date || 'n/a'}</div>
              <div>Price: ${insight.price.toFixed(2)}</div>
              <div>P/S: {insight.sales_multiple?.toFixed(2) ?? 'n/a'}</div>
              <div>PEG: {insight.peg?.toFixed(2) ?? 'n/a'}</div>
            </div>
            <div className="criteria">
              <span className={insight.narrative_shift ? 'pass' : 'fail'}>
                Narrative shift
              </span>
              <span className={insight.cheap_on_sales ? 'pass' : 'fail'}>
                Cheap on sales
              </span>
              <span className={insight.multi_theme_exposure ? 'pass' : 'fail'}>
                Multi-theme exposure
              </span>
              <span className={insight.ecosystem_halo ? 'pass' : 'fail'}>
                Ecosystem halo
              </span>
              <span className={insight.peg_value ? 'pass' : 'fail'}>PEG &lt; 1</span>
              <span className={insight.technical_confirmed ? 'pass' : 'fail'}>
                Technical confirm
              </span>
            </div>
            <ul>
              {insight.highlights.map((highlight, idx) => (
                <li key={idx}>{highlight}</li>
              ))}
            </ul>
          </div>
        ))
      )}
    </div>
  );
};

export default InflectionInsights;
