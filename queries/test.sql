SELECT
    'ONGOING' AS 'ENDORSEMENT TAGGING',
    'S.P. MADRID' AS 'AGENCY',
    CASE 
	    WHEN SUBSTRING_INDEX(debtor.`product_description`, ':', -1) IS NULL THEN "Teacher's Loan"
	    ELSE SUBSTRING_INDEX(debtor.`product_description`, ':', -1)
    END AS 'PRODUCTS',
    SUBSTRING_INDEX(debtor.`placement`, ':', 1) AS 'BUCKET',
    DATE_FORMAT(debtor.`assign_date`, '%c/%e/%Y') AS 'ENDORSEMENT DATE',
    debtor.`account` AS 'LOAN ACCOUNT NUMBER',
    debtor.`name` AS 'ACCOUNT NAME',
    debtor.`aging` AS 'DPD',
    debtor.`balance` AS 'OUTSTANDING BALANCE',
    COALESCE(ptp_status.`status_code`, latest_remark.`status_code`, 'Account No Effort') AS 'STATUSCODE',
    
    CASE 
        WHEN latest_remark.remark LIKE '%SMS with content%' OR latest_remark.`status_code` = 'BULK SMS SENT'
            THEN CONCAT(
                DATE_FORMAT(latest_remark.datetime, '%c/%e/%Y'), 
                ' SMS sent'
            )
        WHEN latest_remark.`status_code` = 'EMAIL - EMAIL BLAST'
            THEN CONCAT(
                DATE_FORMAT(latest_remark.datetime, '%c/%e/%Y'), 
                ' EMAIL sent'
            )
        WHEN latest_remark.remark IS NULL AND latest_remark.status_code IS NULL
            THEN ''
        ELSE CONCAT(DATE_FORMAT(latest_remark.datetime, '%c/%e/%Y'), ' ', latest_remark.remark)
    END AS 'DATE I CALL RESULT',
    
    debtor.`old_ic` AS 'Old IC'

FROM debtor

LEFT JOIN contact_number ON contact_number.`debtor_id` = debtor.`id`
LEFT JOIN contact_number_type ON contact_number_type.`id` = contact_number.`contact_number_type_id`

-- Subquery for latest PTP status (even if older)
LEFT JOIN (
    SELECT 
        df_ptp.debtor_id,
        followup_ptp.`status_code`,
        followup_ptp.remark,
        followup_ptp.datetime
    FROM debtor_followup df_ptp
    INNER JOIN followup followup_ptp ON followup_ptp.id = df_ptp.followup_id
    INNER JOIN (
        SELECT 
            df_ptp2.debtor_id,
            MAX(followup_ptp2.datetime) AS max_ptp_datetime
        FROM debtor_followup df_ptp2
        INNER JOIN followup followup_ptp2 ON followup_ptp2.id = df_ptp2.followup_id
        WHERE DATE(followup_ptp2.datetime) <= CURDATE()
            AND followup_ptp2.`status_code` IN ('PTP - INSTALLMENT', 'PTP - PARTIAL PAYMENT', 'PTP - FULL UPDATE', 'PTP - FULLY PAID')
        GROUP BY df_ptp2.debtor_id
    ) latest_ptp ON latest_ptp.debtor_id = df_ptp.debtor_id 
        AND latest_ptp.max_ptp_datetime = followup_ptp.datetime
) ptp_status ON ptp_status.debtor_id = debtor.id

-- Subquery for latest remark (from ANY valid followup)
LEFT JOIN (
    SELECT 
        df_remark.debtor_id,
        followup_remark.`status_code`,
        followup_remark.remark,
        followup_remark.datetime
    FROM debtor_followup df_remark
    INNER JOIN followup followup_remark ON followup_remark.id = df_remark.followup_id
    INNER JOIN (
        SELECT 
            df_remark2.debtor_id,
            MAX(followup_remark2.datetime) AS max_remark_datetime
        FROM debtor_followup df_remark2
        INNER JOIN followup followup_remark2 ON followup_remark2.id = df_remark2.followup_id
        WHERE DATE(followup_remark2.datetime) <= CURDATE()
            AND followup_remark2.`status_code` NOT IN ('NEW', 'ABORT', 'BUSY', 'BP', 'ABORT', 'SMS FAILED', 'RNA', 'DROPPED', 'SMS REPLY', 'SMS Replied')
            AND followup_remark2.remark NOT LIKE '%Account has been reactive%'
            AND followup_remark2.remark NOT LIKE '%Updates when case reassign to another collector%'
        GROUP BY df_remark2.debtor_id
    ) latest_remark_valid ON latest_remark_valid.debtor_id = df_remark.debtor_id 
        AND latest_remark_valid.max_remark_datetime = followup_remark.datetime
) latest_remark ON latest_remark.debtor_id = debtor.id

WHERE debtor.client_id = 112
    AND debtor.`is_aborted` = 0
    AND debtor.`is_locked` = 0
    -- AND (
    --     debtor.`old_ic` LIKE '%MBGS%' OR
    --     debtor.`old_ic` LIKE '%MBGBSL%' OR
    --     debtor.`old_ic` LIKE '%MMFL%' OR
    --     debtor.`old_ic` LIKE '%MBRL%'
    -- )

GROUP BY debtor.`old_ic`
ORDER BY latest_remark.datetime DESC;