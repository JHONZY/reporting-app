SELECT
    DATE_FORMAT(MAX(followup.`datetime`), '%m/%d/%Y') AS `DATE`,
    debtor.`account` AS `PN`,
    debtor.`name` AS `NAME`,
    debtor.`old_ic` AS `OLD IC`,
    GROUP_CONCAT(
	    DISTINCT
            CONCAT(
            DATE_FORMAT(followup.`datetime`, '%m/%d/%Y'), " ",
                CASE 
                    WHEN followup.status_code IN ('SMS SENT', 'BULK SMS SENT') THEN 'SMS Sent'
                    WHEN followup.status_code IN ('EMAIL - EMAIL BLAST') THEN 'EMAIL Sent'
                    ELSE followup.remark
            END
	    )
	    ORDER BY followup.`datetime` DESC 
	    SEPARATOR ', '
	) AS `COLLECTION_REMARKS`,
    
    'SPM' AS `AGENCY`,
    MAX(followup.`datetime`) AS `Latest Barcode Date`
    
FROM debtor
LEFT JOIN debtor_followup ON debtor_followup.`debtor_id` = debtor.`id`
LEFT JOIN followup ON followup.`id` = debtor_followup.`followup_id`
LEFT JOIN contact_number ON contact_number.`debtor_id` = debtor.`id`
LEFT JOIN contact_number_type ON contact_number_type.`id` = contact_number.`contact_number_type_id`

WHERE debtor.client_id = 112
    AND followup.`datetime` BETWEEN '2026-03-01' AND DATE_FORMAT(NOW(), '%Y-%m-%d 23:59:59')
    AND debtor.`is_aborted` = 0
    AND followup.`status_code` NOT IN ('NEW', 'SMS FAILED', 'ABORT', 'BP')
    AND followup.remark NOT LIKE '%New files imported%'
    AND followup.remark NOT LIKE '%New Assignment - OS%'
    AND followup.remark NOT LIKE '%Account has been reactive%'
    AND followup.remark NOT LIKE '%predictive call automatically detected%'
    AND followup.remark NOT LIKE '%Updates when case reassign to another collector%'
    AND followup.remark NOT LIKE '%System Auto Update Remarks For PD%' 
    
GROUP BY debtor.`old_ic`
ORDER BY MAX(followup.`datetime`) DESC;