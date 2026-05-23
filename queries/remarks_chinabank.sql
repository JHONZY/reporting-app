SELECT
    DATE_FORMAT(MAX(followup.`datetime`), '%m/%d/%Y') AS `DATE`,
    debtor.`account` AS `PN`,
    debtor.`name` AS `NAME`,

    GROUP_CONCAT(
        DISTINCT UPPER(
            CASE

                -- SMS SENT
                WHEN followup.`status_code` = 'SMS SENT' THEN
                    CONCAT(
                        DATE_FORMAT(followup.`datetime`, '%m/%d/%Y'),
                        '-SENT MESSAGE SMS'
                    )

                -- BULK SMS SENT
                WHEN followup.`status_code` = 'BULK SMS SENT' THEN
                    CONCAT(
                        DATE_FORMAT(followup.`datetime`, '%m/%d/%Y'),
                        '-SENT MESSAGE SMS'
                    )

                -- PREDICTIVE CALL / RNA
                WHEN followup.`remark` LIKE '%Predictive CP110849 called%'
                    OR followup.`status_code` = 'RNA' THEN
                    CONCAT(
                        DATE_FORMAT(followup.`datetime`, '%m/%d/%Y'),
                        '-',
                        REPLACE(followup.`contact_number`, '+63', '0'),
                        ' | RFD: UNCONTACTABLE | SRC: CALL | SPMADRID - RINGING NO ANSWER'
                    )

                -- BUSY
                WHEN followup.`status_code` = 'BUSY' THEN
                    CONCAT(
                        DATE_FORMAT(followup.`datetime`, '%m/%d/%Y'),
                        '-',
                        REPLACE(followup.`contact_number`, '+63', '0'),
                        ' | RFD: UNCONTACTABLE | SRC: CALL | SPMADRID - BUSY'
                    )

                -- DEFAULT REMARK
                ELSE
                    REPLACE(
                        REPLACE(
                                CONCAT(
                                    DATE_FORMAT(followup.`datetime`, '%m/%d/%Y'),
                                    "-",
                                    followup.`remark`
                            ),
                            '1_', ''
                        ),
                        '0_', ''
                    )

            END
        )
        ORDER BY followup.`datetime` DESC SEPARATOR ' | '
    ) AS `COLLECTION_REMARKS`,

    'SPM' AS `AGENCY`

FROM debtor

LEFT JOIN contact_number 
    ON contact_number.`debtor_id` = debtor.`id`

LEFT JOIN contact_number_type 
    ON contact_number_type.`id` = contact_number.`contact_number_type_id`

LEFT JOIN debtor_followup 
    ON debtor_followup.`debtor_id` = debtor.`id`

LEFT JOIN followup 
    ON followup.`id` = debtor_followup.`followup_id`

WHERE debtor.`client_id` = 113
AND debtor.`account_type` <> 'WRITEOFF'
AND followup.`remark` NOT LIKE '%BEG PTP%'

AND followup.`datetime` BETWEEN '2026-01-01' AND DATE_FORMAT(NOW(), '%Y-%m-%d 23:59:59')

AND (
        debtor.`is_aborted` = 0
        OR (
            debtor.`is_aborted` = 1
            AND debtor.`abort_date` BETWEEN
                DATE_FORMAT(
                    NOW(),
                    '%Y-%m-%d 00:00:00'
                )
                AND DATE_FORMAT(
                    NOW(),
                    '%Y-%m-%d 23:59:59'
                )
        )
    )

AND debtor.`id` IN (
        SELECT DISTINCT debtor_followup.`debtor_id`
        FROM debtor_followup
        INNER JOIN followup
            ON followup.id = debtor_followup.followup_id
        WHERE debtor_followup.debtor_id = debtor.id
        AND DATE(followup.`datetime`) = CURDATE()
    )

AND followup.`status_code` NOT IN ('NEW', 'SMS FAILED', 'REACTIVE')

AND followup.remark NOT LIKE '%New files imported%'
AND followup.remark NOT LIKE '%New Assignment - OS%'
AND followup.remark NOT LIKE '%Updates when case reassign to another collector%'
AND followup.remark NOT LIKE '%System Auto Update Remarks%'
AND followup.remark NOT LIKE '%System Auto Update Remarks For PD%'
AND followup.remark NOT LIKE '%New Contact Details Added%'

GROUP BY debtor.`account`

ORDER BY MAX(followup.`datetime`) DESC;