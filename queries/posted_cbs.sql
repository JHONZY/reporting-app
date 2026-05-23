SELECT
    debtor.`client_name` AS `CLIENT NAME`,
    debtor.`old_ic` AS `CH`,
    DATE_FORMAT(debtor.`assign_date`, '%m/%d/%Y') AS `ENDO DATE`,
    SUBSTRING_INDEX(debtor.`account`, '_', 1) AS `PN NUMBER`,
    debtor.`name` AS `ACCOUNT NAME`,
    debtor.`balance` AS `OB`,
    
    CASE 
        WHEN debtor_followup.`claim_paid_date` IS NULL THEN DATE_FORMAT(debtor_followup.`ptp_date`, '%m/%d/%Y')
        ELSE DATE_FORMAT(debtor_followup.`claim_paid_date`, '%m/%d/%Y')
    END AS `PTP DATE`,
    
    CASE 
        WHEN debtor_followup.`claim_paid_amount` is null then debtor_followup.`ptp_amount`
        else debtor_followup.`claim_paid_amount`
    end as `PTP_AMOUNT`,
    
    CASE    
        WHEN followup.`remark` LIKE '%WALKIN%' THEN 'SPMADRID'
        WHEN followup.`remark` LIKE '%WALK IN%' THEN 'SPMADRID'
        WHEN followup.`remark` LIKE '%WALK-IN%' THEN 'SPMADRID'
        WHEN followup.`remark` LIKE '%WALK- IN%' THEN 'SPMADRID'
        WHEN followup.`remark` LIKE '%WALK - IN%' THEN 'SPMADRID'
        WHEN followup.`remark` LIKE '%WALK -IN%' THEN 'SPMADRID'
        ELSE followup.`remark_by`
    END AS `COLLECTOR`,
    
    TRIM(SUBSTRING_INDEX(followup.status_code, ' - ', 1)) AS `STATUS`,
    TRIM(SUBSTRING_INDEX(followup.status_code, ' - ', -1)) AS `SUBSTATUS`,
    
    followup.`remark` AS `REMARKS`

FROM debtor
INNER JOIN debtor_followup ON debtor_followup.`debtor_id` = debtor.`id`
INNER JOIN followup ON followup.`id` = debtor_followup.`followup_id`
    
WHERE debtor.client_id = 98
    AND SUBSTRING_INDEX(followup.`status_code`, '-', 1) = 'PAYMENT'
    AND (
        (debtor_followup.`claim_paid_date` BETWEEN '{start_date}' AND '{end_date}')
        OR
        (debtor_followup.`ptp_date` BETWEEN '{start_date}' AND '{end_date}')
    )
    {status_filter}
    
ORDER BY `PTP DATE` DESC;