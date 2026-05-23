SELECT
    DATE_FORMAT(debtor.`assign_date`, '%c/%e/%Y') AS 'ENDORSEMENT DATE',
    'SP MADRID' AS 'AGENCY',
    -- COLLECTOR it shoulld look up using account PN look up here   "\\192.168.15.241\admin\ACTIVE\jlborromeo\CBS APD\CBS APD - STATUS REPORT TEMPLATE.xlsx" sheet name is "hierarchy"  look up value in hierarchy is in O Column then return value is  P column then if blanks then use this followup.`remark_by`
    followup.`remark_by` AS 'COLLECTOR NAME',
    debtor.`card_no` AS 'ACCOUNT NUMBER',
    debtor.`account` AS 'PN',
    debtor.`name` AS 'ACCOUNT NAME',
    '08 ED - APDS LOAN' AS 'PRODUCT DESCRIPTION',
    debtor.`balance` AS 'OB',
    debtor.`monthly_instalment` AS 'MO. AMORT',


    (SELECT 
        CASE
            WHEN debtor_followup.`ptp_amount` IS NULL THEN debtor_followup.`claim_paid_amount`
            ELSE debtor_followup.`ptp_amount`
        END
        FROM debtor_followup
        INNER JOIN followup ON followup.id = debtor_followup.followup_id
        WHERE debtor_followup.debtor_id = debtor.id
        AND SUBSTRING_INDEX(followup.`status_code`, ' - ', 1) IN ('PTP','PTP NEW')
        AND followup.`status_code` NOT IN ('FOLLOW UP - KOR', 'FOLLOW UP - DP')
        AND followup.remark NOT LIKE '%New files imported%'
        AND followup.remark NOT LIKE '%New Assignment - OS%'
        AND followup.remark NOT LIKE '%Updates when case reassign to another collector%'
        AND followup.`datetime` BETWEEN DATE_FORMAT(NOW(), '%Y-%m-01 00:00:00') AND DATE_FORMAT(NOW() - INTERVAL 1 DAY, '%Y-%m-%d 23:59:59')
        ORDER BY followup.`datetime` DESC
        LIMIT 1
    ) AS 'PTP AMOUNT',

    -- PTP_ACQUIRED: earliest PTP barcode date in the filtered date range
    (
        SELECT DATE_FORMAT(MIN(followup.`datetime`), '%m/%d/%Y')
        FROM debtor_followup
        INNER JOIN followup ON followup.id = debtor_followup.followup_id
        WHERE debtor_followup.debtor_id = debtor.id
          AND followup.remark NOT LIKE '%New files imported%'
          AND followup.remark NOT LIKE '%New Assignment - OS%'
          AND followup.remark NOT LIKE '%Updates when case reassign to another collector%'
          AND SUBSTRING_INDEX(followup.`status_code`, ' - ', 1) IN ('PTP', 'POSITIVE CONTACT')
          AND (
		debtor_followup.`ptp_amount` IS NOT NULL
		OR debtor_followup.`claim_paid_amount` IS NOT NULL
		)
          AND followup.`datetime` BETWEEN DATE_FORMAT(DATE(NOW()),'%Y-%m-01 00:00:00')
                                             AND DATE_FORMAT(DATE(NOW()+INTERVAL 1 MONTH),'%Y-%m-1 23:59:59')-INTERVAL 1 DAY
                                             #AND leads_result.leads_result_barcode_date BETWEEN '2025-12-01 00:00:00' AND '2025-12-31 23:59:59'
    ) AS 'PTP_ACQUIRED',

    (SELECT UPPER(followup.`remark`)
        FROM debtor_followup
        INNER JOIN followup ON followup.id = debtor_followup.followup_id
        WHERE debtor_followup.debtor_id = debtor.id
          AND SUBSTRING_INDEX(followup.`status_code`, ' - ', 1) IN ('PTP','PTP NEW')
          AND (
		debtor_followup.`ptp_amount` IS NOT NULL
		OR debtor_followup.`claim_paid_amount` IS NOT NULL
		)
        ORDER BY followup.`datetime` DESC
        LIMIT 1
    ) AS 'REMARKS',
    
    (SELECT 
        CASE
            WHEN debtor_followup.`ptp_date` IS NULL THEN DATE_FORMAT(debtor_followup.`claim_paid_date`, '%c/%e/%Y')
            ELSE DATE_FORMAT(debtor_followup.`ptp_date`, '%c/%e/%Y')
        END
        FROM debtor_followup
        INNER JOIN followup ON followup.id = debtor_followup.followup_id
        WHERE debtor_followup.debtor_id = debtor.id
        AND SUBSTRING_INDEX(followup.`status_code`, ' - ', 1) IN ('PTP','PTP NEW')
        AND followup.`status_code` NOT IN ('FOLLOW UP - KOR', 'FOLLOW UP - DP')
        AND followup.remark NOT LIKE '%New files imported%'
        AND followup.remark NOT LIKE '%New Assignment - OS%'
        AND followup.remark NOT LIKE '%Updates when case reassign to another collector%'
        AND followup.`datetime` BETWEEN DATE_FORMAT(NOW(), '%Y-%m-01 00:00:00') AND DATE_FORMAT(NOW() - INTERVAL 1 DAY, '%Y-%m-%d 23:59:59')
        ORDER BY followup.`datetime` DESC
        LIMIT 1
    ) AS 'PTP DATE',
    -- Final bucket it shoulld look up using account PN look up here   "\\192.168.15.241\admin\ACTIVE\jlborromeo\CBS APD\CBS APD - STATUS REPORT TEMPLATE.xlsx" sheet name is "DATABASE"  look up value in database is in B Column then return value is  G column then if blanks then use this  debtor.`account_type`
    debtor.`account_type` AS 'BUCKET',
    followup.`status_code`
    
FROM debtor

-- LEFT JOIN contact_number ON contact_number.`debtor_id` = debtor.`id`
-- LEFT JOIN contact_number_type ON contact_number_type.`id` = contact_number.`contact_number_type_id`
LEFT JOIN debtor_followup ON debtor_followup.`debtor_id` = debtor.`id`
LEFT JOIN followup ON followup.`id` = debtor_followup.`followup_id`

WHERE debtor.`client_id` = 113
AND debtor.`account_type` <> 'WRITEOFF'
AND followup.`status_code` NOT IN ('FOLLOW UP - KOR', 'FOLLOW UP - DP')
AND followup.remark NOT LIKE '%New files imported%'
AND followup.remark NOT LIKE '%New Assignment - OS%'
AND followup.remark NOT LIKE '%Updates when case reassign to another collector%'
AND followup.`datetime` BETWEEN DATE_FORMAT(NOW(), '%Y-%m-01 00:00:00') AND DATE_FORMAT(NOW() - INTERVAL 1 DAY, '%Y-%m-%d 23:59:59')
AND SUBSTRING_INDEX(followup.`status_code`, ' - ', 1) IN ('PTP','PTP NEW','FOLLOW UP')
	


  
GROUP BY debtor.`account`
ORDER BY followup.`datetime` ASC;