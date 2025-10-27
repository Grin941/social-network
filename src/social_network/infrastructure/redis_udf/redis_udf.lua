#!lua name=chat_functions

local function make_dialog(keys, args)
    -- Формат ключа: dialog:user_id:friend_id
    local key = keys[1]
    local chat_data = args[1]

    redis.call('SET', key, chat_data)

    return 'OK'
end

local function get_dialog(keys, args)
    -- Формат ключа: dialog:user_id:friend_id
    local key = keys[1]
    return redis.call('GET', key)
end

local function write_message(keys, args)
    -- Формат ключа: messages:dialog_id
    local key = keys[1]
    local message = args[1]
    local timestamp = tonumber(args[2])

    redis.call('ZADD', key, timestamp, message)

    return 'OK'
end

local function show_messages(keys, args)
    -- Формат ключа: messages:dialog_id
    local key = keys[1]
    local offset = tonumber(args[1]) or 0
    local limit = tonumber(args[2]) or -1

    if limit >= 0 then
        limit = offset + limit - 1
    end

    return messages = redis.call('ZRANGE', key, offset, limit)
end

redis.register_function('make_dialog', make_dialog)
redis.register_function('get_dialog', get_dialog)
redis.register_function('write_message', write_message)
redis.register_function('show_messages', show_messages)
