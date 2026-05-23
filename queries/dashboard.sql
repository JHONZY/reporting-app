SELECT 
    DATE(debtor.`assign_date`) AS date, 
    COUNT(DISTINCT debtor.`old_ic`) AS active_accounts,
    SUM(debtor.`balance`) AS total_balance
FROM debtor
WHERE debtor.`client_id` = {client_id}
    {user_condition_filter}
GROUP BY DATE(debtor.`assign_date`)
ORDER BY DATE(debtor.`assign_date`);