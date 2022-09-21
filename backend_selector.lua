local function select_backend(txn)
    -- Get the frontend that was used
    local fe_name = txn.f:fe_name()

    local least_sessions_backend = ""
    local least_sessions = 99999999999

    local elec_prices = { ['fi1'] = 308.1, ['de1'] = 50 }
    local cheapest = get_min_price(elec_prices)
    cheapest = call_api()
    core.log(core.debug, "DONE WITH CALL API")

    -- Loop through all the backends. You could change this
    -- so that the backend names are passed into the function too.
    for backend_name, backend in pairs(core.backends) do
        local total_sessions = 0

        -- Using the backend, loop through each of its servers
        for _, server in pairs(backend.servers) do

            -- Get server's stats
            local stats = server:get_stats()

            -- Get the backend's total number of current sessions
            -- TODO: change this to consider elec price info?
            if stats['status'] == 'UP' then
                total_sessions = total_sessions + stats['scur']
                core.Debug(backend.name .. ": " .. total_sessions)
            end
        end
        
        if least_sessions > total_sessions then
            least_sessions = total_sessions
            least_sessions_backend = backend.name
        end

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

core.register_fetches('selected_backend', select_backend)