from iac_analysis.resource import ResourceMetric


def compute_constraints(resource, solver, all_resources):
    match resource.name:
        case "Lambda123":
            lambda_monthly_requests = solver.nv(
                resource, ResourceMetric.monthly_requests
            )
            resource_b = all_resources["ResourceB"]
            lambda_to_b_monthly_requests = solver.ev(
                resource, resource_b, ResourceMetric.monthly_requests
            )
            solver.add(3 * lambda_monthly_requests == lambda_to_b_monthly_requests)
