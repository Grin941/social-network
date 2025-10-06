SELECT create_time_partitions(table_name:= 'chat_messages',
    partition_interval:= '1 day',
    end_at:= '2025-10-30',
    start_from:= '2025-10-01');

SELECT create_distributed_table('chat_messages', 'chat_id', 'hash');
