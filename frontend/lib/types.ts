export interface User {
  id: string;
  email: string;
  is_verified: boolean;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface JobInputs {
  recipient_email?: string | null;
  addresses: string[];
  interest_rate: number;
  years: number;
  discount_percentage: number;
  closing_costs_input: number;
  money_down_input: number;
  operating_expenses_input: number;
  additional_annual_income_input: number;
  vacancy_allowance_percent_input: number;
  lender_ltv_input: number;
  rehab_costs_est_input: number;
  refi_loan_amount_input: number;
  refi_closing_costs_est_input: number;
  num_months_holding: number;
}

export interface Job {
  id: string;
  status: string;
  source_url: string | null;
  inputs: JobInputs & Record<string, unknown>;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface JobFile {
  id: string;
  file_type: string;
  filename: string;
  s3_key: string | null;
  created_at: string;
}

export interface FileDownload {
  url: string;
  expires_in: number;
  filename: string;
}

export interface Subscription {
  status: string;
  plan_id: string | null;
  current_period_end: string | null;
}

export interface CheckoutSession {
  checkout_url: string;
}

export const DEFAULT_JOB_INPUTS: JobInputs = {
  addresses: [""],
  interest_rate: 0.06,
  years: 30,
  discount_percentage: 0.25,
  closing_costs_input: 0.04,
  money_down_input: 0.2,
  operating_expenses_input: 0.02,
  additional_annual_income_input: 0,
  vacancy_allowance_percent_input: 0.05,
  lender_ltv_input: 0.75,
  rehab_costs_est_input: 0.25,
  refi_loan_amount_input: 0.5,
  refi_closing_costs_est_input: 0.04,
  num_months_holding: 3,
};
