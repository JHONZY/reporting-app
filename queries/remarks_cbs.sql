#SET SESSION group_concat_max_len = 20000;

SELECT
    debtor.`account` AS `PN`,
    debtor.`old_ic` as `CHCODE`,
    GROUP_CONCAT(
        DISTINCT UPPER(

            CASE

                /* =========================
                   SMS / BULK SMS FORMAT
                ==========================*/
                WHEN followup.status_code IN ('SMS SENT', 'BULK SMS SENT')
                THEN TRIM(
                        REGEXP_REPLACE(
                            CONCAT(
                                DATE_FORMAT(followup.`datetime`, '%c.%e.%Y'),
                                ' SMS_SPMADRID 09772961780 SEND SMS TEMPLATE'
                            ),
                            '[[:space:]]+',
                            ' '
                        )
                     )

                /* =========================
                   NORMAL REMARKS
                ==========================*/
                ELSE

                    TRIM(
                        REGEXP_REPLACE(

                            CONCAT(

                                /* DATE FROM SYSTEM */
                                DATE_FORMAT(followup.`datetime`, '%c.%e.%Y'),
                                ' ',

                                /* CLEAN REMARK */
                                REGEXP_REPLACE(

                                    TRIM(
                                        REPLACE(
                                            REPLACE(
                                                REPLACE(

                                                    CASE
                                                        WHEN followup.`remark` LIKE '%[RWH]%'
                                                            OR followup.`remark` LIKE '%[DSL]%'
                                                            OR followup.`remark` LIKE '%[ETO]%'
                                                            OR followup.`remark` LIKE '%[RIO]%'
                                                            OR followup.`remark` LIKE '%[PLW]%'
                                                            OR followup.`remark` LIKE '%[BDS]%'
                                                            OR followup.`remark` LIKE '%[BCP]%'
                                                            OR followup.`remark` LIKE '%[BFE]%'
                                                            OR followup.`remark` LIKE '%[BCT]%'
                                                            OR followup.`remark` LIKE '%[SCP]%'
                                                            OR followup.`remark` LIKE '%[DRP]%'
                                                            OR followup.`remark` LIKE '%[RRP]%'
                                                            OR followup.`remark` LIKE '%[JUE]%'
                                                            OR followup.`remark` LIKE '%[CMP]%'
                                                            OR followup.`remark` LIKE '%[DFI]%'
                                                            OR followup.`remark` LIKE '%[HSM]%'
                                                            OR followup.`remark` LIKE '%[DIF]%'
                                                            OR followup.`remark` LIKE '%[FTE]%'
                                                            OR followup.`remark` LIKE '%[DCD]%'
                                                            OR followup.`remark` LIKE '%[SIR]%'
                                                            OR followup.`remark` LIKE '%[TOI]%'
                                                            OR followup.`remark` LIKE '%[SNR]%'
                                                            OR followup.`remark` LIKE '%[SLR]%'
                                                            OR followup.`remark` LIKE '%[ASN]%'
                                                            OR followup.`remark` LIKE '%[ASL]%'
                                                            OR followup.`remark` LIKE '%[MUP]%'
                                                            OR followup.`remark` LIKE '%[BFF]%'
                                                            OR followup.`remark` LIKE '%[ODD]%'
                                                            OR followup.`remark` LIKE '%[OCH]%'
                                                            OR followup.`remark` LIKE '%[QLT]%'
                                                            OR followup.`remark` LIKE '%[CRU]%'
                                                            OR followup.`remark` LIKE '%[RFD]%'
                                                            OR followup.`remark` LIKE '%[CFP]%'
                                                        THEN SUBSTRING_INDEX(followup.`remark`, '|', 1)

                                                        ELSE followup.`remark`
                                                    END,

                                                    '- Inserted By API', ''
                                                ),
                                                '1_', ''
                                            ),
                                            '0_', ''
                                        )
                                    ),

                                    /* REMOVE OLD DATE IF PRESENT */
                                    '^[0-9]{1,2}/[0-9]{1,2}/([0-9]{4}|[0-9]{2})[[:space:]]*',
                                    ''
                                )
                            ),

                            /* FIX DOUBLE SPACES */
                            '[[:space:]]+',
                            ' '
                        )
                    )

            END
        )

        ORDER BY followup.`datetime` DESC
        SEPARATOR ' | '

    ) AS COLLECTION_REMARKS,
    MAX(followup.`datetime`) AS `Latest Barcode Date`

FROM debtor

LEFT JOIN contact_number
    ON contact_number.`debtor_id` = debtor.`id`

LEFT JOIN contact_number_type
    ON contact_number_type.`id` = contact_number.`contact_number_type_id`

LEFT JOIN debtor_followup
    ON debtor_followup.`debtor_id` = debtor.`id`

LEFT JOIN followup
    ON followup.`id` = debtor_followup.`followup_id`

WHERE debtor.client_id = 98
    AND debtor.`is_aborted` = 0
    -- AND debtor.`is_locked` = 0

    AND followup.`datetime`
        BETWEEN DATE_FORMAT(NOW(), '2026-01-01')
        AND DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 DAY), '%Y-%m-%d 23:59:59')

    AND SUBSTRING_INDEX(followup.status_code, ' - ', -1)
        NOT IN ('PUSHBACK', 'FLOWED', 'PULLED_OUT')

    AND followup.`remark` NOT LIKE '%WALKIN%'
    AND followup.`remark` NOT LIKE '%WALK IN%'
    AND followup.`remark` NOT LIKE '%WALK-IN%'
    AND followup.`remark` NOT LIKE '%WALK- IN%'
    AND followup.`remark` NOT LIKE '%WALK - IN%'
    AND followup.`remark` NOT LIKE '%WALK -IN%'

    AND followup.`remark` NOT LIKE 'New Assignment - OS updated from'
    AND followup.status_code <> 'TEST STATUS'
    AND followup.remark NOT LIKE '%Broadcast%'
    AND followup.remark NOT LIKE '%Updates when case reassign to another collector%'
    AND followup.remark NOT LIKE '%System Auto Update Remarks For PD%'
    AND followup.remark NOT LIKE '%REACTIVE%'
    AND followup.remark NOT LIKE '%Broken Promise%'
    AND followup.remark NOT LIKE '%New files imported%'
    AND followup.remark NOT LIKE '%New Assignment - OS Updated from%'

    AND followup.status_code NOT IN (
        'DNC - FLOWED',
        'ABORT',
        'Field Visit Request',
        'NEW',
        'RNA',
        'PP'
    )

GROUP BY debtor.`old_ic`

ORDER BY `Latest Barcode Date` DESC;