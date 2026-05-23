SELECT 
    followup.`remark_by` AS agent,
    COUNT(CASE WHEN TRIM(SUBSTRING_INDEX(followup.`status_code`, '-', 1)) = 'PAYMENT' THEN 1 END) AS posted_count,
    SUM(CASE WHEN TRIM(SUBSTRING_INDEX(followup.`status_code`, '-', 1)) = 'PAYMENT' THEN debtor_followup.`claim_paid_amount` ELSE 0 END) AS posted_amount,
    COUNT(CASE WHEN TRIM(SUBSTRING_INDEX(followup.`status_code`, '-', 1)) = 'PTP' THEN 1 END) AS ptp_count,
    SUM(CASE WHEN TRIM(SUBSTRING_INDEX(followup.`status_code`, '-', 1)) = 'PTP' THEN debtor_followup.`ptp_amount` ELSE 0 END) AS ptp_amount,
    COUNT(CASE WHEN DATE(debtor_followup.`claim_paid_date`) = CURDATE() THEN 1 END) AS posted_today_count,
    SUM(CASE WHEN DATE(debtor_followup.`claim_paid_date`) = CURDATE() THEN debtor_followup.`claim_paid_amount` ELSE 0 END) AS posted_today_amount
FROM debtor
INNER JOIN debtor_followup ON debtor_followup.`debtor_id` = debtor.`id`
INNER JOIN followup ON followup.`id` = debtor_followup.`followup_id`
WHERE debtor.`client_id` = {client_id}
    AND TRIM(SUBSTRING_INDEX(followup.`status_code`, '-', 1)) IN ('PTP', 'PAYMENT')
    AND (debtor_followup.`ptp_date` IS NOT NULL OR debtor_followup.`claim_paid_date` IS NOT NULL)
    AND debtor.`is_aborted` = 0
    AND followup.`datetime` BETWEEN DATE_FORMAT(NOW(), '%Y-%m-01 00:00:00') AND DATE_FORMAT(NOW(), '%Y-%m-%d 23:59:59')
    {extra_condition}
GROUP BY followup.`remark_by`
ORDER BY posted_amount DESC
LIMIT 10;