use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3_stub_gen::define_stub_info_gatherer;
use pyo3_stub_gen::derive::gen_stub_pyfunction;

#[pyfunction]
#[gen_stub_pyfunction]
fn fib(val: u64) -> u64 {
    if val < 2 {
        return 1;
    }
    fib(val - 1) + fib(val - 2)
}


#[pymodule]
#[pyo3(name = "native")]
fn native(m: &Bound<PyModule>) -> PyResult<()> {

    m.add_function(wrap_pyfunction!(fib, m)?)?;
    Ok(())
}

define_stub_info_gatherer!(stub_info);
