import Lake
open Lake DSL

require "leanprover-community" / "mathlib" @ git "v4.29.1"

package «ObserverPatchHolography» where
  leanOptions := #[
    ⟨`autoImplicit, false⟩,
    ⟨`relaxedAutoImplicit, false⟩,
    ⟨`pp.unicode.fun, true⟩
  ]

@[default_target]
lean_lib «ObserverPatchHolography» where

@[default_target]
lean_lib «ObservableNormalForms» where
  srcDir := "ObservableNormalForms"

lean_exe «oph» where
  root := `Main
