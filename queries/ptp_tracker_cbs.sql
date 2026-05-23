SELECT
    'SPM' AS `AGENCY`,
    CONCAT("'", SUBSTRING_INDEX(debtor.`account`, '_', 1)) AS `PN NUMBER`,
    debtor.`name` AS `ACCT NAME`,
    debtor.`balance` AS `OB`,
    debtor.`product_type` AS "BUCKET",
    CASE 
        WHEN debtor_followup.`ptp_date` IS NULL THEN DATE_FORMAT(debtor_followup.`claim_paid_date`, '%m/%d/%Y')
        ELSE DATE_FORMAT(debtor_followup.`ptp_date`, '%m/%d/%Y')
    END AS `PAYMENT DATE`,
   
    (SELECT 
        CASE 
            WHEN SUBSTRING_INDEX(followup.`status_code`, ' - ', 1) = "PAYMENT" THEN SUBSTRING_INDEX(followup.`status_code`, ' - ', -1)
            ELSE ""
        END
        FROM debtor_followup
        INNER JOIN followup ON followup.id = debtor_followup.followup_id
        WHERE debtor_followup.debtor_id = debtor.id
        ORDER BY followup.`datetime` DESC
        LIMIT 1
    ) AS `STATUS IF PAID`,
    
    (SELECT 
        CASE 
            WHEN SUBSTRING_INDEX(followup.`status_code`, ' - ', 1) = "BP" THEN "BP"
            WHEN SUBSTRING_INDEX(followup.`status_code`, ' - ', 1) = "PAYMENT" THEN "PAID"
            ELSE "PENDING"
        END
        FROM debtor_followup
        INNER JOIN followup ON followup.id = debtor_followup.followup_id
        WHERE debtor_followup.debtor_id = debtor.id
        ORDER BY followup.`datetime` DESC
        LIMIT 1
    ) AS `PAID / BP`,

    "" AS "DATE PAID"

FROM debtor
INNER JOIN debtor_followup ON debtor_followup.`debtor_id` = debtor.`id`
INNER JOIN followup ON followup.`id` = debtor_followup.`followup_id`
    
WHERE debtor.client_id = 98
    AND SUBSTRING_INDEX(followup.`status_code`, ' - ', 1) IN ("PAYMENT", "PTP", "BP")
    AND (
        DATE(debtor_followup.`claim_paid_date`) BETWEEN 
            STR_TO_DATE('{start_date}', '%m/%d/%Y')
            AND STR_TO_DATE('{end_date}', '%m/%d/%Y')
        OR
        DATE(debtor_followup.`ptp_date`) BETWEEN 
            STR_TO_DATE('{start_date}', '%m/%d/%Y')
            AND STR_TO_DATE('{end_date}', '%m/%d/%Y')
    )

GROUP BY debtor.`account`
ORDER BY `PAYMENT DATE` DESC;