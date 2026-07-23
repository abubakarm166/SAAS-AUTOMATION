/** Default financial inputs — keep in sync with frontend/lib/types.ts */
const DEFAULT_JOB_INPUTS = {
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

if (typeof globalThis !== "undefined") {
  globalThis.DEFAULT_JOB_INPUTS = DEFAULT_JOB_INPUTS;
}
