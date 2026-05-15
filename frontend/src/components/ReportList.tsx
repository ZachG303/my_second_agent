import React from 'react';
import { fetchReports } from '../services/api';

interface Report {
  company_ticker: string;
  report_date: string;
  report_type: string;
}

const ReportList: React.FC = () => {
  const [reports, setReports] = React.useState<Report[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const loadReports = async () => {
      try {
        const data = await fetchReports(10);
        setReports(data);
      } catch (error) {
        console.error('Failed to fetch reports:', error);
      } finally {
        setLoading(false);
      }
    };
    loadReports();
  }, []);

  if (loading) return <div>Loading reports...</div>;

  return (
    <div className="report-list">
      <h2>Recent Earnings Reports</h2>
      <ul>
        {reports.map((report) => (
          <li key={`${report.company_ticker}-${report.report_date}`}>
            {report.company_ticker} - {report.report_date} ({report.report_type})
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ReportList;
