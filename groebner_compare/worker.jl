# Persistent Groebner.jl F4 adapter. Packages: Groebner, AbstractAlgebra, JSON3.
# The Python parent independently certifies every returned Boolean basis.
using Groebner, AbstractAlgebra, JSON3

function run_worker()
    ring = nothing
    variables = nothing
    identity = nothing
    trace = nothing
    support = nothing
    for line in eachline(stdin)
        request = JSON3.read(line)
        response = Dict{String,Any}("request_id" => request.request_id)
        try
            redirect_stdout(stderr) do
                current = (String(request.encoding), String(request.ring.field),
                           String(request.ring.order), String(request.ring.quotient),
                           Tuple(String.(request.ring.variables)))
                if ring === nothing
                    ring, variables = polynomial_ring(GF(2), collect(current[5]),
                                                       internal_ordering=:degrevlex)
                    identity = current
                end
                current == identity || error("ring/encoding identity changed")
                polynomials = typeof(ring(0))[]
                for row in request.instance.equations
                    polynomial = ring(0)
                    for mask in row
                        monomial = ring(1)
                        for i in eachindex(variables)
                            if (Int(mask) & (1 << (i - 1))) != 0
                                monomial *= variables[i]
                            end
                        end
                        polynomial += monomial
                    end
                    push!(polynomials, polynomial)
                end
                append!(polynomials, [x^2 + x for x in variables])
                shape = [[Tuple(e) for e in exponent_vectors(f)] for f in polynomials]
                operation = String(request.operation)
                basis = nothing
                if operation == "learn"
                    trace, basis = groebner_learn(polynomials, ordering=DegRevLex(),
                                                 linalg=:deterministic)
                    support = shape
                    response["trace_id"] = "session-trace-1"
                elseif operation == "apply"
                    if trace === nothing || String(request.trace_id) != "session-trace-1" || shape != support
                        response["status"] = "incompatible"
                        response["reason"] = "trace or canonical generator supports differ"
                        return
                    end
                    flag, basis = groebner_apply!(trace, polynomials)
                    if !flag
                        response["status"] = "incompatible"
                        response["reason"] = "Groebner.jl apply rejected the trace"
                        return
                    end
                elseif operation == "solve"
                    basis = groebner(polynomials, ordering=DegRevLex(), linalg=:deterministic)
                else
                    error("unknown operation")
                end
                # Quotient by x_i^2+x_i, cancelling duplicate masks in GF(2).
                rows = Vector{Int}[]
                for polynomial in basis
                    parity = Set{Int}()
                    for exponents in exponent_vectors(polynomial)
                        mask = sum((1 << (i - 1)) for i in eachindex(exponents)
                                   if exponents[i] > 0; init=0)
                        if mask in parity
                            delete!(parity, mask)
                        else
                            push!(parity, mask)
                        end
                    end
                    push!(rows, sort!(collect(parity)))
                end
                response["status"] = "ok"
                response["basis_terms"] = rows
                response["solver_version"] = string(pkgversion(Groebner))
                response["julia_version"] = string(VERSION)
                response["threads"] = Threads.nthreads()
                response["metrics"] = Dict()
            end
        catch exception
            response["status"] = "error"
            response["reason"] = sprint(showerror, exception)
        end
        println(JSON3.write(response))
        flush(stdout)
    end
end

run_worker()
