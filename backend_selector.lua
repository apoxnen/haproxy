local function select_backend(txn)
    -- Get the frontend that was used
    local fe_name = txn.f:fe_name()

    local least_sessions_backend = "de1"
    local least_sessions = 99999999999

    local cheapest = "de1"
    cheapest = call_redis()
    core.log(core.debug, "DONE WITH CALL REDIS")

    -- Loop through all the backends. You could change this
    -- so that the backend names are passed into the function too.
    for backend_name, backend in pairs(core.backends) do
        if backend_name == cheapest then
            core.log(core.debug, "FOUND CHEAPEST, RETURNING...")
            return backend.name
        end
    end

    -- Return the name of the backend that has the fewest sessions
    core.Debug("Returning: " .. least_sessions_backend)
    return least_sessions_backend
end

-- Helper function for getting the cheapest price
function get_min_price(t)
    local key = next(t)
    local min = t[key]

    for k, v in pairs(t) do
        if t[k] < min then
            key, min = k, v
        end
    end
    return key
end

function call_api()
    core.log(core.debug, "CALL API")
    local http = require("socket.http")
    --local cjson = require("cjson")
    local requestString = "http://host.docker.internal:9000"
    local body, code = http.request(requestString)
    if body == nil then
        body = "EMPTY BODY"
    end
    core.log(core.debug, body)
    -- TODO: response body is not json
    -- local jsonDict = cjson.decode(body)
    return body
end

function call_redis()
    core.log(core.debug, "CALL REDIS")
    local REDIS = require("redis")
    local redis = REDIS.connect('host.docker.internal', 6379)
    local v = redis:get("cheapest")
    return v
end

core.register_fetches('selected_backend', select_backend)