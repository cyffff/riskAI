// Mock data for development and when API is unavailable
export const mockData = {
  features: [
    {
      id: 1,
      name: "Credit Score",
      description: "Customer credit score from credit bureau",
      data_type: "NUMBER",
      is_active: true,
      category: "Credit Risk",
      importance_score: 0.85,
      computation_logic: "Direct feed from credit bureau",
      tags: [
        { id: 1, name: "Credit" },
        { id: 2, name: "Core" }
      ],
      created_at: "2023-01-15T10:30:00Z",
      updated_at: "2023-04-20T14:45:00Z"
    },
    {
      id: 2,
      name: "Income to Debt Ratio",
      description: "Ratio of customer income to total debt",
      data_type: "FLOAT",
      is_active: true,
      category: "Affordability",
      importance_score: 0.76,
      computation_logic: "income / total_debt",
      tags: [
        { id: 3, name: "Income" },
        { id: 4, name: "Ratio" }
      ],
      created_at: "2023-01-18T11:20:00Z",
      updated_at: "2023-05-12T09:15:00Z"
    },
    {
      id: 3,
      name: "Previous Defaults",
      description: "Number of previous defaults in the last 24 months",
      data_type: "INTEGER",
      is_active: false,
      category: "Credit History",
      importance_score: 0.68,
      computation_logic: "COUNT(defaults WHERE date > NOW() - 24 MONTHS)",
      tags: [
        { id: 5, name: "Historical" },
        { id: 6, name: "Delinquency" }
      ],
      created_at: "2023-02-05T15:45:00Z",
      updated_at: "2023-03-18T10:30:00Z"
    }
  ],
  
  sqlSets: [
    {
      id: 1,
      name: "Core Risk Metrics",
      description: "SQL queries for calculating core risk metrics",
      is_active: true,
      created_at: "2023-01-10T09:15:00Z",
      updated_at: "2023-05-15T14:30:00Z",
      sql_statements: [
        {
          id: 1,
          name: "Credit Utilization",
          sql_type: "SELECT",
          is_active: true
        },
        {
          id: 2,
          name: "Default Frequency",
          sql_type: "SELECT",
          is_active: true
        }
      ]
    },
    {
      id: 2,
      name: "Fraud Detection",
      description: "SQL queries for fraud detection and analysis",
      is_active: true,
      created_at: "2023-02-20T11:45:00Z",
      updated_at: "2023-04-10T16:20:00Z",
      sql_statements: [
        {
          id: 3,
          name: "Suspicious Transactions",
          sql_type: "SELECT",
          is_active: true
        }
      ]
    },
    {
      id: 3,
      name: "Legacy Models",
      description: "SQL queries used by legacy risk models",
      is_active: false,
      created_at: "2022-11-05T10:30:00Z",
      updated_at: "2023-03-22T09:45:00Z",
      sql_statements: []
    }
  ],
  
  sqlStatements: [
    {
      id: 1,
      name: "Credit Utilization",
      statement: "SELECT customer_id, SUM(balance) / SUM(credit_limit) AS utilization_ratio\nFROM credit_accounts\nWHERE status = 'active'\nGROUP BY customer_id\nHAVING utilization_ratio > :threshold",
      sql_type: "SELECT",
      is_active: true,
      sql_set_id: 1,
      metadata: {
        parameters: [
          { name: "threshold", type: "float", default_value: "0.7", required: true }
        ],
        columns: ["customer_id", "utilization_ratio"],
        description: "Calculates credit utilization ratio for customers"
      },
      created_at: "2023-01-12T14:20:00Z",
      updated_at: "2023-04-18T11:15:00Z"
    },
    {
      id: 2,
      name: "Default Frequency",
      statement: "SELECT customer_id, COUNT(*) AS default_count\nFROM loan_events\nWHERE event_type = 'default'\nAND event_date > DATEADD(month, -:months, CURRENT_DATE)\nGROUP BY customer_id",
      sql_type: "SELECT",
      is_active: true,
      sql_set_id: 1,
      metadata: {
        parameters: [
          { name: "months", type: "integer", default_value: "24", required: true }
        ],
        columns: ["customer_id", "default_count"],
        description: "Counts defaults within specified months"
      },
      created_at: "2023-01-15T09:30:00Z",
      updated_at: "2023-05-10T15:45:00Z"
    },
    {
      id: 3,
      name: "Suspicious Transactions",
      statement: "SELECT t.transaction_id, t.customer_id, t.amount, t.transaction_date\nFROM transactions t\nJOIN (\n  SELECT customer_id, AVG(amount) * :multiplier AS threshold\n  FROM transactions\n  WHERE transaction_date > DATEADD(day, -90, CURRENT_DATE)\n  GROUP BY customer_id\n) avg_t ON t.customer_id = avg_t.customer_id\nWHERE t.amount > avg_t.threshold\nAND t.transaction_date > DATEADD(day, -:days, CURRENT_DATE)",
      sql_type: "SELECT",
      is_active: true,
      sql_set_id: 2,
      metadata: {
        parameters: [
          { name: "multiplier", type: "float", default_value: "3.0", required: true },
          { name: "days", type: "integer", default_value: "30", required: true }
        ],
        columns: ["transaction_id", "customer_id", "amount", "transaction_date"],
        description: "Identifies transactions that exceed average amount by specified multiplier"
      },
      created_at: "2023-02-22T13:45:00Z",
      updated_at: "2023-04-15T10:20:00Z"
    }
  ]
}; 